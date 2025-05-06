from gerber_renderer import Gerber


gbr = "D:/github/project/MyCNC/file/simple_2layer-F_Cu.gbr"

board = Gerber.Board(gbr, verbose=True)
board.render('output')


