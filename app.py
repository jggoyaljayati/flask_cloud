from flask import Flask, Response, request
import pandas as pd

app = Flask(__name__)
data = pd.read_csv("Classification Results on Face Dataset (1000 images).csv")

@app.route("/", methods=['POST'])
def home():
    try:
        file = request.files['inputFile']
        filename = file.filename[:-4]
        result = data[data['Image'] == filename].Results.item()

        return Response(("{}:{}").format(filename, result), status=200, mimetype='application/json')

    except Exception as e:
        return Response(f"Error: {str(e)}", status=400, mimetype='application/json')

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
