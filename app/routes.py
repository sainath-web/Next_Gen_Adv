from flask import request, jsonify
from models.opportunity import Opportunity
from models.dealer import Dealer
from models.account import Account
from config.database import get_session
from datetime import datetime
from sqlalchemy.exc import IntegrityError
import uuid

# Helper function to get the opportunity stage
def get_opportunity_stage(probability):
    if 10 <= probability <= 20:
        return "Prospecting"
    elif 21 <= probability <= 40:
        return "Qualification"
    elif 41 <= probability <= 60:
        return "Needs Analysis"
    elif 61 <= probability <= 70:
        return "Value Proposition"
    elif 71 <= probability <= 80:
        return "Decision Makers"
    elif 81 <= probability <= 85:
        return "Perception Analysis"
    elif 86 <= probability <= 90:
        return "Proposal/Price Quote"
    elif 91 <= probability <= 95:
        return "Negotiation/Review"
    elif probability == 100:
        return "Closed Won"
    elif probability == 0:
        return "Closed Lost"
    else:
        return "Unknown Stage"

# Helper function to convert the amount to multiple currencies
def get_currency_conversion(amount):
    usd_rate = 0.012  # Example rate
    aud_rate = 0.018  # Example rate
    cad_rate = 0.016  # Example rate

    usd = round(amount * usd_rate, 2)
    aud = round(amount * aud_rate, 2)
    cad = round(amount * cad_rate, 2)

    return usd, aud, cad

import requests

# def get_currency_conversion(amount):
#     # Replace 'YOUR_API_KEY' with your actual API key
#     api_url = 'https://v6.exchangerate-api.com/v6/YOUR_API_KEY/latest/USD'
    
#     try:
#         response = requests.get(api_url)
#         response.raise_for_status()  # Check for HTTP errors
#         data = response.json()
        
#         # Get the conversion rates
#         usd_rate = 1  # Since the base currency is USD, the rate is 1 for USD
#         aud_rate = data['conversion_rates']['AUD']
#         cad_rate = data['conversion_rates']['CAD']
        
#         # Convert amounts
#         usd = round(amount * usd_rate, 2)
#         aud = round(amount * aud_rate, 2)
#         cad = round(amount * cad_rate, 2)
        
#         return usd, aud, cad
    
#     except requests.RequestException as e:
#         print(f"Error fetching currency data: {e}")
#         # Return default values or handle error
#         return 0, 0, 0

# Sign up for an account with the chosen API service to get your API key.
# Replace 'YOUR_API_KEY' in the URL with your actual key.




def init_routes(app):
    session = get_session()
    @app.route('/new_customer', methods=['POST'])
    def create_new_customer():
        payload = request.get_json()
        
        # Create unique ID for the new opportunity
        opportunity_id = str(uuid.uuid4())
                
        # Check if account exists
        account_name = payload.get('account_name')
        account = session.query(Account).filter_by(account_name=account_name).first()
        if not account:
            return jsonify({"error": "Account does not exist"}), 400
        
        # Check if dealer exists and the details match
        dealer_id = payload.get('dealer_id')
        dealer_code = payload.get('dealer_code')
        opportunity_owner = payload.get('dealer_name_or_opportunity_owner')

        dealer = session.query(Dealer).filter(
            Dealer.dealer_id == dealer_id,
            Dealer.dealer_code == dealer_code,
            Dealer.opportunity_owner == opportunity_owner
        ).first()

        if not dealer:
            return jsonify({"error": "Dealer validation failed"}), 401
        
        # Calculate opportunity stage based on probability
        probability = payload.get('probability', 0)
        opportunity_stage = get_opportunity_stage(probability)

        # Convert amount to multiple currencies
        amount = payload.get('amount', 0)
        usd, aud, cad = get_currency_conversion(amount)

        # Insert opportunity if validations pass
        try:
            new_opportunity = Opportunity(
                opportunity_id=opportunity_id,
                opportunity_name=payload['opportunity_name'],
                account_name=payload['account_name'],
                close_date=payload['close_date'],
                amount=payload['amount'],
                description=payload['description'],
                dealer_id=payload['dealer_id'],
                dealer_code=payload['dealer_code'],
                dealer_name_or_opportunity_owner=payload['dealer_name_or_opportunity_owner'],
                stage=payload['stage'],
                probability=payload['probability'],
                next_step=payload['next_step'],
                amount_usd=usd,  # Converted amount to USD
                amount_aud=aud,  # Converted amount to AUD
                amount_cad=cad,  # Converted amount to CAD
                # created_date=datetime.now()
            )
            session.add(new_opportunity)
            session.commit()
            return jsonify({"message": "Customer created successfully", "opportunity_id": opportunity_id}), 201
        except IntegrityError:
            session.rollback()
            return jsonify({"error": "Failed to create opportunity"}), 500

    @app.route('/get_customers', methods=['GET'])
    def get_all_customers():
        dealer_id = request.args.get('dealer_id')
        dealer_code = request.args.get('dealer_code')
        opportunity_owner = request.args.get('opportunity_owner')

        # Validate dealer information
        dealer = session.query(Dealer).filter(
            Dealer.dealer_id == dealer_id,
            Dealer.dealer_code == dealer_code,
            Dealer.opportunity_owner == opportunity_owner
        ).first()

        print(dealer)

        if not dealer:
            return jsonify({"error": "Dealer validation failed"}), 401
        
        # Fetch all opportunities for this dealer
        opportunities = session.query(Opportunity).filter(
            Opportunity.dealer_code == dealer_code
        ).all()
        
        if not opportunities:
            return jsonify({"message": "No opportunities found"}), 404
        
        return jsonify([opportunity.to_dict() for opportunity in opportunities]), 200


    @app.route('/single_customer', methods=['GET'])
    def get_single_customer():
        dealer_id = request.args.get('dealer_id')
        dealer_code = request.args.get('dealer_code')
        opportunity_owner = request.args.get('opportunity_owner')
        opportunity_id = request.args.get('opportunity_id')

        # Validate dealer information
        dealer = session.query(Dealer).filter(
            Dealer.dealer_id == dealer_id,
            Dealer.dealer_code == dealer_code,
            Dealer.opportunity_owner == opportunity_owner
        ).first()

        if not dealer:
            return jsonify({"error": "Dealer validation failed"}), 401
        
        # Fetch the specific opportunity
        opportunity = session.query(Opportunity).filter_by(opportunity_id=opportunity_id).first()
        
        if not opportunity:
            return jsonify({"message": "Opportunity not found"}), 404
        
        return jsonify(opportunity.to_dict()), 200
    
    # POST Route for Service Updates
    @app.route('/service_update', methods=['POST'])
    def create_service_update():
        data = request.get_json()
        customer_id = data.get('customer_id')
        service_date = data.get('service_date')
        update_description = data.get('update_description')
        status = data.get('status')
        
        if not all([customer_id, service_date, update_description, status]):
            return jsonify({"error": "Missing required fields"}), 400
        
        new_update = ServiceUpdate(
            customer_id=customer_id,
            service_date=service_date,
            update_description=update_description,
            status=status
        )
        session.add(new_update)
        session.commit()
        
        return jsonify({"message": "Service update created successfully", "id": new_update.id}), 201
    
# GET Route for Service Updates
    @app.route('/service_update/<int:update_id>', methods=['GET'])
    def get_service_update(update_id):
        update = session.query(ServiceUpdate).filter_by(id=update_id).first()
        if update:
            return jsonify({
                "customer_id": update.customer_id,
                "service_date": update.service_date.isoformat(),
                "update_description": update.update_description,
                "status": update.status
            }), 200
        return jsonify({"error": "Service update not found"}), 404

    # POST Route for Customer Reviews
    @app.route('/customer_review', methods=['POST'])
    def create_customer_review():
        data = request.get_json()
        customer_id = data.get('customer_id')
        review_date = data.get('review_date')
        rating = data.get('rating')
        review_text = data.get('review_text')
        
        if not all([customer_id, review_date, rating is not None, review_text]):
            return jsonify({"error": "Missing required fields"}), 400
        
        if not (1 <= rating <= 5):
            return jsonify({"error": "Rating must be between 1 and 5"}), 400
        
        new_review = CustomerReview(
            customer_id=customer_id,
            review_date=review_date,
            rating=rating,
            review_text=review_text
        )
        session.add(new_review)
        session.commit()
        
        return jsonify({"message": "Customer review created successfully", "id": new_review.id}), 201

    # GET Route for Customer Reviews

    @app.route('/customer_review/<int:review_id>', methods=['GET'])
    def get_customer_review(review_id):
        review = session.query(CustomerReview).filter_by(id=review_id).first()
        if review:
            return jsonify({
                "customer_id": review.customer_id,
                "review_date": review.review_date.isoformat(),
                "rating": review.rating,
                "review_text": review.review_text
            }), 200
        return jsonify({"error": "Customer review not found"}), 404









