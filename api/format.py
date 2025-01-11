import os
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_restx import Api, Resource, Namespace, fields, reqparse
import logging
import toolPath
import stp_to_stl
from opencamlib import ocl
import stl_scale
import path_algorithm

logging.disable(logging.CRITICAL)

# 初始化 Flask 应用
app = Flask(__name__)

# 初始化 Flask-RESTX API
api = Api(app, version='1.0', title='Sample API',
          description='A sample API', doc='/docs'
          )

# CORS 配置
CORS(app, resources=r'/*')

# 创建命名空间
cam_ns = Namespace('api', description='Tool path generation')

# 注册命名空间到 API
api.add_namespace(cam_ns)

upload_parser = reqparse.RequestParser()
upload_parser.add_argument(
    'file',
    location='files',
    type='FileStorage',
    required=True,
    help='The file to be uploaded'
)


# stp转stl
@cam_ns.route("/stp2stl")
@cam_ns.expect(upload_parser)
@cam_ns.doc(
    description="To facilitate threejs rendering and opencam generating tool paths",
    params={
        'linear_deflection': {
            'description': 'control linear deviation, smaller, more detailed the grid.',
            'type': float,  # 文件的 ID，类型为整型
            'default': 0.01,  # 设置默认值为 1
            'required': False  # 可选参数
        },
        'angular_deflection': {
            'description': 'Control Angle deviation, smaller, more accurate the curvature representation of the surface.',
            'type': float,  # 文件的 ID，类型为整型
            'default': 0.5,  # 设置默认值为 1
            'required': False  # 可选参数
        },
        'file': {
            'description': 'The stp file to be uploaded (required)',
            'type': 'file',  # 类型为文件
            'required': True  # 必填项
        }
    },
    responses={
        200: 'File uploaded successfully, and tool path is returned.',
        400: 'Invalid file format or no file uploaded.',
    },
)
class stp2stl(Resource):
    def post(self):
        """
        接收 STP 文件返回STL文件
        """
        if 'file' in request.files:
            file = request.files['file']
            file_name = file.filename
            # 判断是否为stp或者step文件
            extensions_name = file_name[file_name.rfind(".") + 1:]
            if extensions_name.lower() not in ['stp', 'step']:
                return {'message': 'Unsupported file type! Only .stp or .step files are allowed.'}, 400
            # 获取参数
            params_dist = request.args.to_dict()
            if params_dist.get("linear_deflection"):
                linear_deflection = float(params_dist.get("linear_deflection"))
            else:
                linear_deflection = 0.01
            if params_dist.get("angular_deflection"):
                angular_deflection = float(params_dist.get("angular_deflection"))
            else:
                angular_deflection = 0.5
            # 删除之前保存的文件
            folder_path = os.path.join(os.getcwd(), 'file')
            for filename in os.listdir(folder_path):
                file_path = os.path.join(folder_path, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)

            # 下载上传的文件，进行转换
            save_path = os.path.join(os.getcwd(), 'file', file_name)
            file.save(save_path)
            shape = stp_to_stl.read_step(save_path)
            stl_file = "./file/" + file_name[0: file_name.rfind(".") + 1] + "stl"
            stp_to_stl.write_stl(shape, stl_file, linear_deflection, angular_deflection)
            return send_file(stl_file, as_attachment=True)

        # 如果没有文件上传，返回错误
        return {'message': 'No file uploaded'}, 400


# stp转stl
@cam_ns.route("/offset_path")
@cam_ns.expect(upload_parser)
@cam_ns.doc(
    description="To facilitate threejs rendering and opencam generating tool paths",
    params={
        'file': {
            'description': 'The stp file to be uploaded (required)',
            'type': 'file',  # 类型为文件
            'required': True  # 必填项
        },
        'z_depth': {
            'description': '',
            'type': float,
            'default': -5,
            'required': True
        },
        'step_over': {
            'description': '',
            'type': float,
            'default': 0.5,
            'required': True
        },
        'diameter': {
            'description': '',
            'type': float,
            'default': 3,
            'required': True
        },
        'tool_type': {
            'description': 'endmill or ball or cone',
            'type': str,
            'default': "endmill",
            'required': True
        },
        'angle': {
            'description': 'only cone have angle',
            'type': float,
            'default': 60,
            'required': False
        },

    },
    responses={
        200: 'File uploaded successfully, and tool path is returned.',
        400: 'Invalid file format or no file uploaded.',
    },
)
class offset_path(Resource):
    def post(self):
        if 'file' in request.files:
            file = request.files['file']
            file_name = file.filename
            # 判断是否为stp或者step文件
            extensions_name = file_name[file_name.rfind(".") + 1:]
            if extensions_name.lower() != 'stl':
                return {'message': 'Unsupported file type! Only stl files are allowed.'}, 400
            # 获取参数

            params_dist = request.args.to_dict()
            if params_dist.get("z_depth"):
                z_depth = float(params_dist.get("z_depth"))
            else:
                return {'message': 'please input z_depth'}, 400

            if params_dist.get("z_depth"):
                z_depth = float(params_dist.get("z_depth"))
            else:
                return {'message': 'please input z_depth'}, 400
            if params_dist.get("step_over"):
                step_over = float(params_dist.get("step_over"))
            else:
                return {'message': 'please input step_over'}, 400
            if params_dist.get("tool_type"):
                tool_type = params_dist.get("tool_type")
                if tool_type.lower() not in ['endmill', 'ball', 'cone']:
                    return {'message': 'Unsupported tool type! Only endmil ,ball, cone are allowed.'}, 400
                if tool_type == "cone":
                    if params_dist.get("angle"):
                        angle = float(params_dist.get("angle"))
                    else:
                        return {'message': 'please input angle'}, 400
            else:
                return {'message': 'please input tool_type'}, 400
            if params_dist.get("diameter"):
                diameter = float(params_dist.get("diameter"))
            else:
                return {'message': 'please input diameter'}, 400

            # 删除之前保存的文件
            folder_path = os.path.join(os.getcwd(), 'file')
            for filename in os.listdir(folder_path):
                file_path = os.path.join(folder_path, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)

            # 下载上传的文件，进行转换
            save_path = os.path.join(os.getcwd(), 'file', file_name)
            file.save(save_path)

            # 解析stl
            surface = toolPath.STLSurfaceSource(save_path)
            # 刀具
            if tool_type == "endmill":
                cutter = ocl.CylCutter(diameter, 10)  # 平底刀
            elif tool_type == "ball":
                cutter = ocl.BallCutter(diameter, 10)  # 球刀
            elif tool_type == "cone":
                cutter = ocl.ConeCutter(diameter, angle, 10)  # 锥形刀

            max_area_point = stl_scale.get_scale(save_path, -10)
            paths = path_algorithm.OffsetPath(max_area_point, diameter, z_depth, layer, step_over)  # 轮廓内部切割路径

            return 1
            # return send_file(stl_file, as_attachment=True)


        # 如果没有文件上传，返回错误
        return {'message': 'No file uploaded'}, 400

# 运行 Flask 应用
if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
