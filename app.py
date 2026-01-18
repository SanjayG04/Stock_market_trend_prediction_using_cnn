from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from config import Config

# Import analysis modules
from modules.technical_analysis import TechnicalAnalyzer
from modules.fundamental_analysis import FundamentalAnalyzer
from modules.scoring_engine import ScoringEngine

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

# Create upload folder if not exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('database', exist_ok=True)

# ==================== DATABASE MODELS ====================

class User(UserMixin, db.Model):
    """User model for authentication"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with analyses
    analyses = db.relationship('Analysis', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        """Verify password"""
        return bcrypt.check_password_hash(self.password_hash, password)


class Analysis(db.Model):
    """Analysis history model"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    stock_ticker = db.Column(db.String(20), nullable=False)
    chart_filename = db.Column(db.String(200))
    
    # Technical analysis results
    technical_trend = db.Column(db.String(20))
    technical_confidence = db.Column(db.Float)
    technical_score = db.Column(db.Float)
    
    # Fundamental analysis results
    pe_ratio = db.Column(db.Float)
    peg_ratio = db.Column(db.Float)
    roe = db.Column(db.Float)
    debt_equity = db.Column(db.Float)
    pb_ratio = db.Column(db.Float)
    fundamental_score = db.Column(db.Float)
    
    # Combined results
    final_score = db.Column(db.Float)
    recommendation = db.Column(db.String(50))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ==================== LOGIN MANAGER ====================

@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login"""
    return User.query.get(int(user_id))


# ==================== HELPER FUNCTIONS ====================

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


# ==================== ROUTES ====================

@app.route('/')
def home():
    """Landing page"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration page"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validation
        if not username or not email or not password:
            flash('All fields are required!', 'danger')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long!', 'danger')
            return render_template('register.html')
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists!', 'danger')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered!', 'danger')
            return render_template('register.html')
        
        # Create new user
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login page"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember', False)
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user, remember=remember)
            flash(f'Welcome back, {user.username}!', 'success')
            
            # Redirect to next page or dashboard
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password!', 'danger')
    
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    """Logout user"""
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard - upload and analyze"""
    return render_template('index.html', username=current_user.username)


@app.route('/analyze', methods=['POST'])
@login_required
def analyze():
    """Process stock analysis"""
    try:
        # Get form data
        stock_ticker = request.form.get('stock_ticker')
        chart_file = request.files.get('chart_image')
        
        if not stock_ticker or not chart_file:
            flash('Please provide both stock ticker and chart image!', 'danger')
            return redirect(url_for('dashboard'))
        
        # Validate file
        if not allowed_file(chart_file.filename):
            flash('Invalid file type! Please upload PNG or JPG image.', 'danger')
            return redirect(url_for('dashboard'))
        
        # Save uploaded file
        filename = secure_filename(f"{current_user.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{chart_file.filename}")
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        chart_file.save(filepath)
        
        # Initialize analyzers
        technical_analyzer = TechnicalAnalyzer(app.config['MODEL_PATH'])
        fundamental_analyzer = FundamentalAnalyzer()
        scoring_engine = ScoringEngine()
        
        # Perform technical analysis
        print(f"Analyzing chart image: {filepath}")
        tech_result = technical_analyzer.predict(filepath)
        
        # Perform fundamental analysis
        print(f"Fetching fundamental data for: {stock_ticker}")
        fund_result = fundamental_analyzer.analyze(stock_ticker)
        
        if not fund_result:
            flash(f'Could not fetch data for ticker: {stock_ticker}. Please check the ticker symbol.', 'warning')
            os.remove(filepath)
            return redirect(url_for('dashboard'))
        
        # Combine scores
        final_result = scoring_engine.combine_scores(tech_result, fund_result)
        
        # Save to database
        analysis = Analysis(
            user_id=current_user.id,
            stock_ticker=stock_ticker,
            chart_filename=filename,
            technical_trend=tech_result['trend'],
            technical_confidence=tech_result['confidence'],
            technical_score=tech_result['score'],
            pe_ratio=fund_result.get('pe_ratio'),
            peg_ratio=fund_result.get('peg_ratio'),
            roe=fund_result.get('roe'),
            debt_equity=fund_result.get('debt_equity'),
            pb_ratio=fund_result.get('pb_ratio'),
            fundamental_score=fund_result['score'],
            final_score=final_result['final_score'],
            recommendation=final_result['recommendation']
        )
        
        db.session.add(analysis)
        db.session.commit()
        
        # Redirect to results page
        return redirect(url_for('results', analysis_id=analysis.id))
        
    except Exception as e:
        print(f"Error during analysis: {str(e)}")
        flash(f'An error occurred during analysis: {str(e)}', 'danger')
        return redirect(url_for('dashboard'))


@app.route('/results/<int:analysis_id>')
@login_required
def results(analysis_id):
    """Display analysis results"""
    analysis = Analysis.query.get_or_404(analysis_id)
    
    # Check if user owns this analysis
    if analysis.user_id != current_user.id:
        flash('Access denied!', 'danger')
        return redirect(url_for('dashboard'))
    
    return render_template('results.html', analysis=analysis)


@app.route('/history')
@login_required
def history():
    """View analysis history"""
    analyses = Analysis.query.filter_by(user_id=current_user.id).order_by(Analysis.created_at.desc()).all()
    return render_template('history.html', analyses=analyses)


@app.route('/delete/<int:analysis_id>', methods=['POST'])
@login_required
def delete_analysis(analysis_id):
    """Delete an analysis"""
    analysis = Analysis.query.get_or_404(analysis_id)
    
    if analysis.user_id != current_user.id:
        flash('Access denied!', 'danger')
        return redirect(url_for('history'))
    
    # Delete chart file
    if analysis.chart_filename:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], analysis.chart_filename)
        if os.path.exists(filepath):
            os.remove(filepath)
    
    db.session.delete(analysis)
    db.session.commit()
    
    flash('Analysis deleted successfully!', 'success')
    return redirect(url_for('history'))


# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500


# ==================== RUN APPLICATION ====================

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create database tables
    app.run(debug=True, host='0.0.0.0', port=5000)
