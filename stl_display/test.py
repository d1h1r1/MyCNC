import triangleCut

save_path = ""
max_area_point, all_scale, detailFlag = triangleCut.get_scale(save_path)

allPath, inOutPath = triangleCut.scalePocket(all_scale, max_area_point, save_path)
