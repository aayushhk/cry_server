from flask import Flask, request, jsonify
from firecrawl import FirecrawlApp
from pydantic import BaseModel
import os

app = Flask(__name__)

# Initialize the FirecrawlApp with your API key
API_KEY = os.getenv('FIRECRAWL_API_KEY', 'fc-c10b9709abf543ec86cf26efcd71b204')
if not API_KEY:
    raise RuntimeError("FIRECRAWL_API_KEY environment variable is not set.")

app_instance = FirecrawlApp(api_key=API_KEY)

class ExtractSchema(BaseModel):
    wallet_address:str
    eth_balance: str
    eth_value: str
    token_holdings:str
    latest_transaction_sent:str
    first_transaction_sent:str
    multichain_portfolio_balance: str
    public_name_tag:str
class ExtractSchematx(BaseModel):
    transaction_hash:str
    transaction_from_address:str
    transaction_from_platform_app:str
    transaction_to_address:str
    transaction_to_platform_app:str
    amount_in_usd:str
    transaction_block_number:str
    transaction_timestamp:str
    transaction_gas_used:str
    transaction_gas_limit:str
    transaction_input:str
    transaction_output:str
    transaction_contract_address:str  



  

def scrape(bc, tx_hash,q,schem):
    if bc == "eth":
        bc_url = 'https://etherscan.io'
    elif bc == "bnb":
        bc_url = 'https://bscscan.com'
    else:
        raise ValueError("Unsupported blockchain")

    etherscan_link = f'{bc_url}/{q}/{tx_hash}'

    data = app_instance.scrape_url(etherscan_link, {
        'formats': ['extract'],
        'extract': {
            'schema': schem.model_json_schema(),
        }
    })
    return data

@app.route('/addx', methods=['GET'])
def get_details_query():
    try:
        # Extract query parameters
        schem=ExtractSchema
        addx = request.args.get("addx")  # Correct parameter name
        bc = request.args.get("bc")  # Correct parameter name

        # Validate the required parameters
        if not addx or not bc:
            return jsonify({"error": "Both addx and bc are required."}), 400

        # Call the scrape function
        q="address"
        result = scrape(bc,addx,q,schem)

        return jsonify({"result": result['extract']}), 200

    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred: " + str(e)}), 500

@app.route('/txn', methods=['GET'])
def get_details():
    try:
        # Extract query parameters
        schem=ExtractSchematx
        addx = request.args.get("txn")  # Correct parameter name
        bc = request.args.get("bc")  # Correct parameter name

        # Validate the required parameters
        if not addx or not bc:
            return jsonify({"error": "Both addx and bc are required."}), 400

        # Call the scrape function
        q="tx"
        result = scrape(bc, addx,q,schem)

        return jsonify({"result": result['extract']}), 200

    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred: " + str(e)}), 500


if __name__ == "__main__":
    try:
        app.run(debug=False, host="0.0.0.0", port=5002)
    except Exception as e:
        print(f"Failed to start the server: {e}")
