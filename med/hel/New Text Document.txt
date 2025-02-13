from flask import Flask, render_template, request
from medical_search_query import MedicalSearchQuery

app = Flask(__name__)

# Initialize the MedicalSearchQuery class
search_query = MedicalSearchQuery("C:/Users/Intel/Documents/med/meddata.csv")

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        input_text = request.form['input_text']
        boolean_query = search_query.get_boolean_query(input_text)
        return render_template('index.html', boolean_query=boolean_query)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)