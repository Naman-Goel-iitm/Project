from flask import Flask, render_template, redirect, url_for, request, flash, Blueprint, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from flask_login import UserMixin
from werkzeug.utils import secure_filename
import os
from alembic import op
import sqlalchemy as sa

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///test.db"
app.config['SECRET_KEY'] = 'thisisasecretkey'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'

db = SQLAlchemy(app)
migrate = Migrate(app, db)

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    role = db.Column(db.String(20))
    is_active = db.Column(db.Boolean, default=True)
    is_flagged = db.Column(db.Boolean, default=False)

# Define the Sponsor model
class Sponsor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    name = db.Column(db.String(100), nullable=False)
    industry = db.Column(db.String(100))
    budget = db.Column(db.Float)
    is_active = db.Column(db.Boolean, default=True)
    is_flagged = db.Column(db.Boolean, default=False)

    campaigns = db.relationship('Campaign', back_populates='sponsor', foreign_keys='Campaign.sponsor_email')


# Define the Influencer model
class Influencer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    name = db.Column(db.String(100), nullable=False)
    platform = db.Column(db.String(100), nullable=False)
    platform_username = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(100))
    niche = db.Column(db.String(100))
    reach = db.Column(db.Integer)
    rating = db.Column(db.Float)
    profile_picture = db.Column(db.String(200), default='default.jpg')  
    is_active = db.Column(db.Boolean, default=True)
    is_flagged = db.Column(db.Boolean, default=False)

    ad_requests = db.relationship('AdRequest', back_populates='influencer')


# Define the Campaign model
class Campaign(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    budget = db.Column(db.Float)
    visibility = db.Column(db.String(10))
    goals = db.Column(db.Text)
    is_flagged = db.Column(db.Boolean, default=False)
    sponsor_email = db.Column(db.String(120), db.ForeignKey('sponsor.email'), nullable=False)
    sponsor = db.relationship('Sponsor', back_populates='campaigns')

    ad_requests = db.relationship('AdRequest', back_populates='campaign')

# Define the AdRequest model
class AdRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'))
    influencer_id = db.Column(db.Integer, db.ForeignKey('influencer.id'))
    messages = db.Column(db.Text)
    requirements = db.Column(db.Text)
    payment_amount = db.Column(db.Float)
    status = db.Column(db.String(20))
    completion_status = db.Column(db.String(20), default='pending')
    request_type = db.Column(db.String(20))  

    campaign = db.relationship('Campaign', back_populates='ad_requests')
    influencer = db.relationship('Influencer', back_populates='ad_requests')

    #Experiment end_________________________________________________________________________

with app.app_context():
    db.create_all()


    
def isduplicate(emailinput):
    duplicate = User.query.filter(
	(User.email == emailinput)
	).first()
    if duplicate:
        return "False"
    else: return "True"


def validate_user(emailinput, passwordinput):
    data_available = User.query.filter(
        (User.email == emailinput)
    ).first()
    pass_available = User.query.filter(
        (User.password == passwordinput)
    ).first()
    # role_admin = User.query.filter(
    #     (User.role == "Admin")
    # ).first()
    if (not(data_available)) or (not(pass_available)):
        return "False"
    else: return "True"


def validate_admin(emailinput, passwordinput, secretinput):
    data_available = User.query.filter(
        (User.email == emailinput)
    ).first()
    pass_available = User.query.filter(
        (User.password == passwordinput)
    ).first()
    # role_admin = User.query.filter(
    #     (User.role == roleinput)
    # ).first()
    
    Secret__key = "BeingNotified"

    # if ((not(data_available)) or (not(pass_available))) or (not(role_admin)):
    #     return "False"
    # else: return "True"

    if (not(data_available and pass_available)): #if any of the one is mismatch then no access
        return"False"
    elif (not(Secret__key == secretinput)): #if role is not admin then condition will be true and it returns false hence no access
        return"False"
    else:
        return "True"
    

@app.route("/")
def Welcome():
    return render_template('Welcome.html')


@app.route("/register", methods=['GET', 'POST'])
def register():
    msg=None
    if request.method=='POST':
        email=(request.form['emailinput'])
        password=(request.form['passwordinput'])
        role=(request.form['roleinput'])
        if ((isduplicate(email)) == "True"):
            param=User(email=email, password=password, role=role)
            db.session.add(param)
            db.session.commit()
            return redirect(url_for('Userlogin'))
        else:
            msg = "Account already Exists"
    return render_template('register.html', msg=msg)

@app.route("/loginrole")
def loginrole():
    return render_template('loginrole.html')


@app.route("/Adminlogin", methods=['GET', 'POST'])
def Adminlogin():
    msg=None
    if request.method=='POST':
        email=(request.form['emailinput'])
        password=(request.form['passwordinput'])
        key=(request.form['secretinput'])
        if ((validate_admin(email, password, key)) == "True"):
            return redirect(url_for('Admindashboard'))
        else:
            msg = "Invalid Credentials"
    return render_template('Adminlogin.html', msg=msg)


@app.route("/Userlogin", methods=['GET', 'POST'])
def Userlogin():
    msg=None
    if request.method=='POST':
        email=(request.form['emailinput'])
        password=(request.form['passwordinput'])
        # role=(request.form['roleinput'])
        if ((validate_user(email, password)) == "True"):
            #test
            user = User.query.filter_by(email=email).first()

            # Clear any existing session data
            session.clear()

            # Set session data
            session['user_email'] = user.email
            session['user_id'] = user.id

            if user.role == 'Sponsor':
                sponsor = Sponsor.query.filter_by(email=user.email).first()
                if not sponsor:
                    # Redirect to profile completion page
                    return redirect(url_for('complete_sponsor_profile'))
                else:
                    # Redirect to sponsor dashboard
                    session['user_email'] = user.email
                    return redirect(url_for('sponsor_dashboard'))
                
            elif user.role == 'Influencer':
                influencer = Influencer.query.filter_by(email=user.email).first()
                if not influencer:
                    #Redirect to profile completion of Influencer
                    return redirect(url_for('complete_influencer_profile'))
                else:
                    #Redirect to Influencer dashboard
                    session['user_email'] = user.email
                    session['influencer_id'] = influencer.id
                    return redirect(url_for('influencer_dashboard'))
                
            elif user.role == 'Admin':
                # Redirect to admin dashboard or other roles
                session['user_id'] = user.id
                return redirect(url_for('AdminDashboard'))
            
            elif user.role == 'Influencer':
                # Redirect to influencer dashboard
                session['user_id'] = user.id
                return redirect(url_for('InfluencerDashboard'))
        else:
            msg = "Invalid Credentials"
    return render_template('Userlogin.html', msg=msg)
            #testend
    #         return redirect(url_for('InfluencerDashboard'))
    #     else:
    #         msg = "Invalid Credentials"
    # return render_template('Userlogin.html', msg=msg)

@app.route("/complete_sponsor_profile", methods=['GET', 'POST'])
def complete_sponsor_profile():
    if request.method == 'POST':
        email = request.form['email']  # Get email from session
        name = request.form['name']
        industry = request.form['industry']
        budget = request.form['budget']

        # Create a new Sponsor object and save it to the database
        new_sponsor = Sponsor(email=email, name=name, industry=industry, budget=float(budget))
        db.session.add(new_sponsor)
        db.session.commit()

        flash('Sponsor profile completed successfully!')
        return redirect(url_for('sponsor_dashboard'))

    # If GET request, render the form
    return render_template('complete_sponsor_profile.html')

@app.route("/complete_influencer_profile", methods=['GET', 'POST'])
def complete_influencer_profile():
    if request.method == 'POST':
        email = request.form['email']  # Get email from session
        name = request.form['name']
        platform = request.form['platform']
        platform_username = request.form['platform_username']
        category = request.form['category']
        niche = request.form['niche']
        reach = request.form['reach']

        # Create a new Influencer object and save it to the database
        new_influencer = Influencer(email=email, name=name, platform=platform, platform_username=platform_username, category=category, niche=niche, reach=reach)
        db.session.add(new_influencer)
        db.session.commit()

        flash('Influencer profile completed successfully!')
        return redirect(url_for('influencer_dashboard'))

    # If GET request, render the form
    return render_template('complete_influencer_profile.html')

@app.route("/edit_influencer_profile", methods=['GET', 'POST'])
def edit_influencer_profile():
    influencer_id = session.get('influencer_id')  # Get the influencer ID from the session
    influencer = Influencer.query.get(influencer_id)  # Get the influencer object from the database

    if request.method == 'POST':
        # Update fields only if they are present in the request form
        if 'name' in request.form and request.form['name']:
            influencer.name = request.form['name']
        
        if 'platform' in request.form and request.form['platform']:
            influencer.platform = request.form['platform']
        
        if 'platform_username' in request.form and request.form['platform_username']:
            influencer.platform_username = request.form['platform_username']
        
        if 'category' in request.form and request.form['category']:
            influencer.category = request.form['category']
        
        if 'niche' in request.form and request.form['niche']:
            influencer.niche = request.form['niche']
        
        if 'reach' in request.form and request.form['reach']:
            influencer.reach = request.form['reach']
        
        # Handle profile picture upload
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file and file.filename:
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                influencer.profile_picture = filename

        # Commit changes to the database
        db.session.commit()

        flash('Your profile has been updated successfully!')
        return redirect(url_for('influencer_dashboard'))

    # If GET request, render the form with existing data
    return render_template('edit_influencer_profile.html', influencer=influencer)


# @app.route("/influencer_dashboard", methods=['GET', 'POST'])
# def influencer_dashboard():
#     return render_template('influencer_dashboard.html')

@app.route('/influencer_dashboard', methods=['GET', 'POST'])
def influencer_dashboard():
    influencer_id = session.get('influencer_id')
    influencer = Influencer.query.get(influencer_id)
    
    if request.method == 'POST':
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file:
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                influencer.profile_picture = filename
                db.session.commit()
                flash('Profile picture updated successfully!')

        if 'name' in request.form:
            influencer.name = request.form['name']
            influencer.platform = request.form['platform']
            influencer.niche = request.form['niche']
            influencer.reach = request.form['reach']
            db.session.commit()
            flash('Profile details updated successfully!')

    # Fetch ad requests for this influencer
    ad_requests = AdRequest.query.filter_by(influencer_id=influencer_id).all()
    
    # Fetch campaign and sponsor details for each ad request
    ad_requests_with_details = []
    for ad_request in ad_requests:
        campaign = Campaign.query.get(ad_request.campaign_id)
        sponsor = Sponsor.query.filter_by(email=campaign.sponsor_email).first()
        ad_requests_with_details.append({
            'ad_request': ad_request,
            'campaign_name': campaign.name,
            'sponsor_name': sponsor.name
            # 'campaign': campaign,
            # 'sponsor': sponsor
        })
    is_flagged = influencer.is_flagged

    return render_template('influencer_dashboard.html', influencer=influencer, ad_requests=ad_requests_with_details, is_flagged=is_flagged)


@app.route('/Admindashboard')
def Admindashboard():
    active_users_count = User.query.filter_by(is_active=True).count()
    public_campaigns_count = Campaign.query.filter_by(visibility='public').count()
    private_campaigns_count = Campaign.query.filter_by(visibility='private').count()
    total_ad_requests_count = AdRequest.query.count()

    flagged_users = User.query.filter_by(is_flagged=True).all()
    active_sponsor_count = db.session.query(User).filter_by(role='Sponsor', is_active=True).count()
    active_influencer_count = db.session.query(User).filter_by(role='Influencer', is_active=True).count()


    return render_template('Admindashboard.html',
                           active_users_count=active_users_count,
                           public_campaigns_count=public_campaigns_count,
                           private_campaigns_count=private_campaigns_count,
                           total_ad_requests_count=total_ad_requests_count,
                           flagged_users=flagged_users,
                           active_sponsors=active_sponsor_count,
                           active_influencers=active_influencer_count)

@app.route('/toggle_flag_user/<int:user_id>', methods=['POST'])
def toggle_flag_user(user_id):
    user = User.query.get_or_404(user_id)
    user.is_flagged = not user.is_flagged
    db.session.commit()
    flash(f"{'Flagged' if user.is_flagged else 'Unflagged'} {user.name}.", 'success')
    return redirect(url_for('Admindashboard'))

@app.route('/flag_campaign/<int:campaign_id>', methods=['POST'])
def flag_campaign(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    campaign.is_flagged = True
    db.session.commit()
    flash('Campaign has been flagged and will not be visible on the Find Campaigns page.', 'success')
    return redirect(url_for('admin_campaigns'))

@app.route('/flag_influencer/<int:influencer_id>', methods=['POST'])
def flag_influencer(influencer_id):
    influencer = Influencer.query.get_or_404(influencer_id)
    influencer.is_flagged = True
    db.session.commit()
    flash('Influencer has been flagged', 'success')
    return redirect(url_for('admin_influencers'))

@app.route('/flag_sponsor/<int:sponsor_id>', methods=['POST'])
def flag_sponsor(sponsor_id):
    sponsor = Sponsor.query.get_or_404(sponsor_id)
    sponsor.is_flagged = True
    db.session.commit()
    flash('sponsor has been flagged', 'success')
    return redirect(url_for('admin_sponsor'))

@app.route('/unflag_campaign/<int:campaign_id>', methods=['POST'])
def unflag_campaign(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    campaign.is_flagged = False
    db.session.commit()
    flash('Campaign has been unflagged and is now visible on the Find Campaigns page.', 'success')
    return redirect(url_for('admin_campaigns'))

@app.route('/unflag_influencer/<int:influencer_id>', methods=['POST'])
def unflag_influencer(influencer_id):
    influencer = Influencer.query.get_or_404(influencer_id)
    influencer.is_flagged = False
    db.session.commit()
    flash('Campaign has been unflagged', 'success')
    return redirect(url_for('admin_influencers'))

@app.route('/unflag_sponsor/<int:sponsor_id>', methods=['POST'])
def unflag_sponsor(sponsor_id):
    sponsor = Sponsor.query.get_or_404(sponsor_id)
    sponsor.is_flagged = False
    db.session.commit()
    flash('sponsor has been unflagged', 'success')
    return redirect(url_for('admin_sponsor'))

@app.route('/delete_campaign_admin/<int:campaign_id>', methods=['POST'])
def delete_campaign_admin(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    db.session.delete(campaign)
    db.session.commit()
    flash('Campaign has been deleted.', 'success')
    return redirect(url_for('admin_campaigns'))

@app.route('/delete_influencer_admin/<int:influencer_id>', methods=['POST'])
def delete_influencer_admin(influencer_id):
    influencer = Influencer.query.get_or_404(influencer_id)
    db.session.delete(influencer)
    db.session.commit()
    flash('Influencer proflie has been deleted.', 'success')
    return redirect(url_for('admin_influencer'))

@app.route('/delete_sponsor_admin/<int:sponsor_id>', methods=['POST'])
def delete_sponsor_admin(sponsor_id):
    sponsor = Sponsor.query.get_or_404(sponsor_id)
    db.session.delete(sponsor)
    db.session.commit()
    flash('sponsor proflie has been deleted.', 'success')
    return redirect(url_for('admin_sponsor'))


#Experimental____________________________________________________________________________
@app.route('/logout')
def logout():
    session.clear()  # Clear all session data
    flash('You have been logged out.')
    return redirect(url_for('Userlogin'))  # Redirect to the login page


@app.route('/dashboard')
def sponsor_dashboard():
    sponsor_id = 1  # Example sponsor_id, replace with actual logged-in sponsor ID
    sponsor = Sponsor.query.get_or_404(sponsor_id)
    # return render_template('sponsor_dashboard.html', sponsor=sponsor, campaigns=sponsor.campaigns)
    user_email = session.get('user_email')  # Get the logged-in user's email from the session
    sponsor = Sponsor.query.filter_by(email=user_email).first()
    campaigns = sponsor.campaigns
    flagged_campaigns = [campaign for campaign in campaigns if campaign.is_flagged]

    is_flagged = sponsor.is_flagged
    return render_template('sponsor_dashboard.html', sponsor=sponsor, campaigns=campaigns, flagged_campaigns=flagged_campaigns, is_flagged=is_flagged)
# <--------------------------------Original end-------------------->

# @app.route('/dashboard')
# def sponsor_dashboard():
#     user_email = session.get('user_email')  # Get the logged-in user's email from the session
    
#     # Retrieve the sponsor associated with the logged-in user
#     sponsor = Sponsor.query.filter_by(email=user_email).first()
    
#     # If the sponsor is flagged, prevent them from seeing any campaigns
#     if sponsor.is_flagged:
#         campaigns = []
#     else:
#         # Query campaigns associated with the sponsor and only those sponsors that are not flagged
#         campaigns = Campaign.query.join(Sponsor, Campaign.sponsor_id == Sponsor.id)\
#                                   .join(User, Sponsor.id == User.sponsor_id)\
#                                   .filter(User.is_flagged == False, Sponsor.email == user_email)\
#                                   .all()
    
#     return render_template('sponsor_dashboard.html', sponsor=sponsor, campaigns=campaigns)

# Define a route to create a new campaign
# @app.route('/create_campaign', methods=['GET', 'POST'])
# def create_campaign():
#     if request.method == 'POST':
#         # Convert string to date object
#         start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d').date()
#         end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d').date()

#         # Create the new Campaign
#         new_campaign = Campaign(
#             name=request.form['name'],
#             description=request.form['description'],
#             start_date=start_date,
#             end_date=end_date,
#             budget=float(request.form['budget']),
#             visibility=request.form['visibility'],
#             goals=request.form['goals'],
#             sponsor_id=1  # Replace with the actual sponsor ID
#         )

#         # Add and commit to the database
#         db.session.add(new_campaign)
#         db.session.commit()
#         flash('Campaign created successfully!')
#         return redirect(url_for('sponsor_dashboard'))
    
#     return render_template('create_campaign.html')
# <---- new route for campaign creation ---->

@app.route('/create_campaign', methods=['GET', 'POST'])
def create_campaign():
    if request.method == 'POST':
        user_email = session.get('user_email')  # Get the logged-in user's email
        sponsor = Sponsor.query.filter_by(email=user_email).first()

        start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d').date()
        end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d').date()

        # Create the new Campaign
        new_campaign = Campaign(
            name=request.form['name'],
            description=request.form['description'],
            start_date=start_date,
            end_date=end_date,
            budget=float(request.form['budget']),
            visibility=request.form['visibility'],
            goals=request.form['goals'],
            sponsor_email=sponsor.email  # Use the correct sponsor_email
        )

        # Add and commit to the database
        db.session.add(new_campaign)
        db.session.commit()
        flash('Campaign created successfully!')
        return redirect(url_for('sponsor_dashboard'))

    return render_template('create_campaign.html')


# Define a route to view all campaigns
@app.route('/view_campaigns')
def view_campaigns():
    campaigns = Campaign.query.all()
    return render_template('view_campaigns.html', campaigns=campaigns)
# <----------------------------Old working Code--------------------------->
# @app.route('/campaign/<int:campaign_id>', methods=['GET', 'POST'])
# def view_campaign_details(campaign_id):
#     # Fetch the campaign details using the campaign ID
#     campaign = Campaign.query.get_or_404(campaign_id)
    
#     # Fetch all ad requests related to this campaign
#     ad_requests = AdRequest.query.filter_by(campaign_id=campaign_id).all()
    
#     return render_template('view_campaign_details.html', campaign=campaign, ad_requests=ad_requests)
# <-----------------------New experiment --------------------------------->

@app.route('/campaign/<int:campaign_id>', methods=['GET', 'POST'])
def view_campaign_details(campaign_id):
    # Fetch the campaign details using the campaign ID
    campaign = Campaign.query.get_or_404(campaign_id)
    
    # Fetch all ad requests related to this campaign
    ad_requests = AdRequest.query.filter_by(campaign_id=campaign_id).all()

    if request.method == 'POST':
        ad_request_id = request.form.get('ad_request_id')
        status = request.form.get('status')

        if ad_request_id and status:
            # Find the ad request and update its status
            ad_request = AdRequest.query.get_or_404(ad_request_id)
            ad_request.status = status
            db.session.commit()
            flash(f'Ad request status updated to {status}', 'success')
            return redirect(url_for('view_campaign_details', campaign_id=campaign_id))
    
    return render_template('view_campaign_details.html', campaign=campaign, ad_requests=ad_requests)

@app.route('/edit_campaign/<int:campaign_id>', methods=['GET', 'POST'])
def edit_campaign(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    if request.method == 'POST':
        if 'name' in request.form and request.form['name']:
            campaign.name = request.form['name']
        if 'description' in request.form and request.form['description']:
            campaign.description = request.form['description']
        if 'start_date' in request.form and request.form['start_date']:
            campaign.start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d').date()
        
        if 'end_date' in request.form and request.form['end_date']:
            campaign.end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d').date()
        if 'budget' in request.form and request.form['budget']:
            campaign.budget = float(request.form['budget'])
        if 'visibility' in request.form and request.form['visibility']:
            campaign.visibility = request.form['visibility']
        if 'goals' in request.form and request.form['goals']:
            campaign.goals = request.form['goals']
        
        # Commit changes to the database
        db.session.commit()
        
        flash('Campaign updated successfully!')
        return redirect(url_for('view_campaign_details', campaign_id=campaign.id))
    
    # If GET request, render the form with existing data
    return render_template('edit_campaign.html', campaign=campaign)

@app.route('/delete_campaign/<int:campaign_id>', methods=['POST'])
def delete_campaign(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)  # Fetch the campaign from the database
    
    # Delete associated details (e.g., AdRequests)
    AdRequest.query.filter_by(campaign_id=campaign_id).delete()
    
    # Delete the campaign
    db.session.delete(campaign)
    db.session.commit()
    
    flash('Campaign deleted successfully!')
    return redirect(url_for('sponsor_dashboard'))


@app.route('/admin_campaigns')
def admin_campaigns():
    campaigns = Campaign.query.all()
    return render_template('admin_campaigns.html', campaigns=campaigns)

@app.route('/admin_influencers')
def admin_influencers():
    influencers = Influencer.query.all()
    return render_template('admin_influencers.html', influencers=influencers)

@app.route('/admin_sponsor')
def admin_sponsor():
    sponsor = Sponsor.query.all()
    return render_template('admin_sponsor.html', sponsor=sponsor)


@app.route('/update_ad_request_status', methods=['POST'])
def update_ad_request_status():
    ad_request_id = request.form.get('ad_request_id')
    status = request.form.get('status')

    if ad_request_id and status:
        # Find the ad request and update its status
        ad_request = AdRequest.query.get_or_404(ad_request_id)
        ad_request.status = status

        if status == 'approved':
            ad_request.completion_status = 'in progress'
        elif status == 'rejected':
            ad_request.completion_status = 'pending'

        db.session.commit()
        flash(f'Ad request status updated to {status}', 'success')
    
    return redirect(url_for('influencer_dashboard'))

@app.route('/update_ad_request_completion_status/<int:ad_request_id>/<string:completion_status>', methods=['POST'])
def update_ad_request_completion_status(ad_request_id, completion_status):
    ad_request = AdRequest.query.get_or_404(ad_request_id)
    ad_request.completion_status = completion_status

    db.session.commit()
    return redirect(url_for('influencer_dashboard'))


@app.route('/edit_ad_request/<int:request_id>', methods=['GET', 'POST'])
def edit_ad_request(request_id):
    ad_request = AdRequest.query.get_or_404(request_id)
    
    if request.method == 'POST':
        ad_request.request_type = request.form['request_type']
        ad_request.messages = request.form['messages']
        ad_request.requirements = request.form['requirements']
        ad_request.amount = request.form['amount']
        ad_request.status = request.form['status']
        ad_request.completion_status = request.form['completion_status']
        
        db.session.commit()
        flash('Ad Request updated successfully!')
        return redirect(url_for('view_campaign_details', campaign_id=ad_request.campaign_id))
    
    return render_template('edit_ad_request.html', ad_request=ad_request)

@app.route('/delete_ad_request/<int:request_id>', methods=['POST'])
def delete_ad_request(request_id):
    ad_request = AdRequest.query.get_or_404(request_id)
    
    campaign_id = ad_request.campaign_id
    
    db.session.delete(ad_request)
    db.session.commit()
    
    flash('Ad Request deleted successfully!')
    return redirect(url_for('view_campaign_details', campaign_id=campaign_id))


@app.route('/find_influencer/<int:campaign_id>')
def find_influencer(campaign_id):
    name = request.args.get('name')
    niche = request.args.get('niche')
    reach = request.args.get('reach')
    
    # influencer_query = Influencer.query
    influencer_query = Influencer.query.filter_by(is_flagged=False)
    
    if name:
        influencer_query = influencer_query.filter(Influencer.name.ilike(f'%{name}%'))
    if niche:
        influencer_query = influencer_query.filter(Influencer.niche.ilike(f'%{niche}%'))
    if reach:
        influencer_query = influencer_query.filter(Influencer.reach >= int(reach))

    # Fetch all influencers from the database
    # influencer = influencer_query.all()
    influencers = influencer_query.all()
    # influencers = User.query.filter_by(role='influencer', is_flagged=False).all()
    return render_template('find_influencer.html', influencers=influencers, campaign_id=campaign_id)
    # Pass the influencers and campaign ID to the template
    # return render_template('find_influencer.html', influencer=influencer, campaign_id=campaign_id)

# @app.route('/request_influencer/<int:campaign_id>/<int:influencer_id>')
# def request_influencer(campaign_id, influencer_id):
#     # Handle the request logic here (e.g., save the request to the database)

#     flash("Request sent successfully!", "success")
#     return redirect(url_for('view_campaign_details', campaign_id=campaign_id))

@app.route('/request_influencer/<int:campaign_id>/<int:influencer_id>', methods=['GET', 'POST'])
def request_influencer(campaign_id, influencer_id):
    if request.method == 'POST':
        # Get form data
        requirements = request.form['requirements']
        messages = request.form['message']
        payment_amount = request.form['payment_amount']
        
        # Create a new AdRequest
        new_ad_request = AdRequest(
            campaign_id=campaign_id,
            influencer_id=influencer_id,
            requirements=requirements,
            messages=messages,
            payment_amount=payment_amount,
            status='pending',
            request_type='Send'
        )
        
        # Save to the database
        db.session.add(new_ad_request)
        db.session.commit()
        
        flash("Request sent successfully!", "success")
        return redirect(url_for('view_campaign_details', campaign_id=campaign_id))
    
    # Render the form if it's a GET request
    return render_template('request_influencer.html')

# @app.route('/find_campaigns')
# def find_campaigns():
#     campaigns = Campaign.query.filter(Campaign.visibility != 'private').all()
#     return render_template('find_campaigns.html', campaigns=campaigns)


@app.route('/find_campaigns')
def find_campaigns():
    campaigns = Campaign.query.filter(Campaign.visibility != 'private', Campaign.is_flagged == False).all()
    return render_template('find_campaigns.html', campaigns=campaigns)


@app.route('/request_campaign/<int:campaign_id>', methods=['GET', 'POST'])
def request_campaign(campaign_id):
    campaign = Campaign.query.get(campaign_id)
    if request.method == 'POST':
        requirements = request.form.get('requirements')
        message = request.form.get('message')
        payment_amount = float(request.form.get('payment_amount'))
        influencer_id = session.get('influencer_id')

        if not all([requirements, message, payment_amount]):
            flash('All fields are required!', 'danger')
            return redirect(url_for('request_campaign', campaign_id=campaign_id))
        
        ad_request = AdRequest(
            campaign_id=campaign.id,
            influencer_id=influencer_id,
            messages=message,
            requirements=requirements,
            payment_amount=payment_amount,
            status='pending',
            completion_status='pending',
            request_type='receive'
        )
        db.session.add(ad_request)
        db.session.commit()
        flash('Request submitted successfully!', 'success')
        return redirect(url_for('influencer_dashboard', campaign_id=campaign_id))

    return render_template('request_campaign.html', campaign=campaign)

@app.route('/campaign_details/<int:campaign_id>')
def campaign_details(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    ad_requests = AdRequest.query.filter_by(campaign_id=campaign_id).all()
    return render_template('campaign_details.html', campaign=campaign, ad_requests=ad_requests)

@app.route('/request_status')
def request_status():
    influencer_id = session.get('influencer_id')
    
    # Fetch all ad requests for this influencer
    ad_requests = AdRequest.query.filter_by(influencer_id=influencer_id).all()
    
    # Prepare a list of campaigns and ad requests
    requests_with_details = []
    for ad_request in ad_requests:
        campaign = Campaign.query.get(ad_request.campaign_id)
        requests_with_details.append({
            'campaign': campaign,
            'ad_request': ad_request
        })

    return render_template('request_status.html', requests_with_details=requests_with_details)



#Experiment Ends_________________________________________________________________________

if __name__ == "__main__":
    app.run(debug=True)