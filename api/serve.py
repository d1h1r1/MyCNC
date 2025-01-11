import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import toolPath

logging.disable(logging.CRITICAL)

app = Flask(__name__)
CORS(app, resources=r'/*')


# 只接受get方法访问
@app.route("/stl_api", methods=['POST'])
def stl_api():
    data = request.form
    # q = data.get('q')
    if 'file' in request.files:
        file = request.files['file']
        file_name = file.filename
        save_path = os.path.join(os.getcwd(), 'file', file_name)
        file.save(save_path)
        path_list = toolPath.get_tool_path(save_path)
        return jsonify(path_list)


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
