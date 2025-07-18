from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
from werkzeug.utils import secure_filename
import os
import sys
import pandas as pd
import time
import json
from collections import Counter
from model.main import process_resume, process_multiple_resumes
import stripe

# Add the current directory to Python path to find the model module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__, 
    static_folder='static',
    template_folder='templates'
)

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize stats
total_resumes = 0
match_rate = 0
processing_time = 0

@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/dashboard')
def dashboard():
    return render_template('index.html')

@app.route('/analyze_single', methods=['POST'])
def analyze_single():
    global total_resumes, match_rate, processing_time
    
    if 'resume' not in request.files:
        return jsonify({'error': 'No resume file uploaded'}), 400
    
    file = request.files['resume']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and file.filename.endswith('.pdf'):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        start_time = time.time()
        try:
            result = process_resume(filepath)
            processing_time = time.time() - start_time
            
            # Update stats with bounded match rate (60-90%)
            total_resumes += 1
            score = result['score'] / 100  # Convert to decimal
            bounded_score = max(0.60, min(0.90, score))  # Ensure score is between 60-90%
            match_rate = (match_rate * (total_resumes - 1) + bounded_score) / total_resumes
            
            # Save results to CSV
            df = pd.DataFrame([result])
            df.to_csv('results.csv', index=False)
            
            return jsonify({'message': 'Analysis completed successfully'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
        finally:
            # Clean up uploaded file
            if os.path.exists(filepath):
                os.remove(filepath)
    
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/analyze_multiple', methods=['POST'])
def analyze_multiple():
    global total_resumes, match_rate, processing_time
    
    if 'resumes' not in request.files:
        return jsonify({'error': 'No resume files uploaded'}), 400
    
    files = request.files.getlist('resumes')
    if not files or files[0].filename == '':
        return jsonify({'error': 'No selected files'}), 400
    
    job_description = request.form.get('job_description', '')
    technologies = request.form.get('technologies', '')
    
    filepaths = []
    try:
        # Save all files
        for file in files:
            if file and file.filename.endswith('.pdf'):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                filepaths.append(filepath)
        
        start_time = time.time()
        results = process_multiple_resumes(filepaths, job_description, technologies)
        processing_time = time.time() - start_time
        
        # Update stats with bounded match rate (60-90%)
        total_resumes += len(results)
        scores = [r['score'] / 100 for r in results]  # Convert to decimal
        bounded_scores = [max(0.60, min(0.90, score)) for score in scores]  # Ensure scores are between 60-90%
        new_match_rate = sum(bounded_scores) / len(results)
        match_rate = (match_rate * (total_resumes - len(results)) + new_match_rate * len(results)) / total_resumes
        
        # Save results to CSV
        df = pd.DataFrame(results)
        df.to_csv('results.csv', index=False)
        
        return jsonify({'message': 'Analysis completed successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        # Clean up uploaded files
        for filepath in filepaths:
            if os.path.exists(filepath):
                os.remove(filepath)

@app.route('/get_results')
def get_results():
    try:
        if os.path.exists('results.csv'):
            return send_file('results.csv', mimetype='text/csv')
        return '', 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_stats')
def get_stats():
    if total_resumes == 0:
        return jsonify({
            'total_resumes': 0,
            'match_rate': 0,
            'processing_time': 0
        })
    
    bounded_rate = max(60, min(90, round(match_rate * 100, 2)))  # Ensure final display is between 60-90%
    return jsonify({
        'total_resumes': total_resumes,
        'match_rate': bounded_rate,
        'processing_time': round(processing_time, 2)
    })

@app.route('/get_tech_trends')
def get_tech_trends():
    try:
        if not os.path.exists('results.csv'):
            return jsonify([])
            
        # Read the results CSV file
        df = pd.read_csv('results.csv')
        
        # Extract technologies from all resumes
        all_technologies = []
        for tech_list in df['technologies'].dropna():
            # Remove quotes and split the string into a list
            technologies = tech_list.strip('"').split(', ')
            all_technologies.extend(technologies)
        
        # Count occurrences of each technology
        tech_counts = Counter(all_technologies)
        total_mentions = sum(tech_counts.values())
        
        # Calculate percentages and determine trends
        tech_data = []
        for tech, count in tech_counts.most_common():
            percentage = round((count / total_mentions) * 100, 1)
            # Determine trend based on percentage
            trend = 'High' if percentage > 12 else ('Medium' if percentage > 8 else 'Low')
            
            tech_data.append({
                'technology': tech,
                'count': count,
                'percentage': percentage,
                'trend': trend
            })
        
        return jsonify(tech_data)
    except Exception as e:
        print(f"Error in get_tech_trends: {str(e)}")
        return jsonify([]), 500

@app.route('/technology')
def technology():
    return render_template('technology.html')

@app.route('/subscription')
def subscription():
    return render_template('subscription.html')

@app.route('/create-checkout-session', methods=['POST'])
def create_checkout():
    try:
        data = request.get_json()
        plan = data.get('plan')
        
        # Define your price IDs for each plan
        price_ids = {
            'basic': 'price_basic_id',  # Replace with your Stripe price ID
            'pro': 'price_pro_id',      # Replace with your Stripe price ID
        }
        
        if plan not in price_ids:
            return jsonify({'error': 'Invalid plan selected'}), 400
            
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': price_ids[plan],
                'quantity': 1,
            }],
            mode='subscription',
            success_url=request.host_url + 'success?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=request.host_url + 'subscription',
        )
        
        return jsonify({'id': checkout_session.id})
    except Exception as e:
        return jsonify({'error': str(e)}), 403

@app.route('/success')
def success():
    return render_template('success.html')

if __name__ == '__main__':
    app.run(debug=True, port=5001) 