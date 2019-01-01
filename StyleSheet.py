class StyleSheet:
        pushButton = 'QPushButton{border: 1px solid grey; border-radius:4px;' \
                                        +'background-color:qlineargradient(spread:pad, x1:0.5, y1:0, x2:0.5, y2:1,'\
                                        +'stop:0.6 rgba(255, 255, 255, 255), stop:0.95 rgb(155, 214, 255),' \
                                        +'stop:0.983425 rgba(255, 255, 255, 255), stop:1 rgba(0, 0, 0, 0))}' \
                            +'QPushButton:pressed{border : 1px solid grey;' \
                                            +'border-radius : 4px;' \
                                            +'background-color: rgb(155, 214, 255)}'\
                            +'QPushButton:checked{border : 1px solid grey;' \
                                            +'border-radius : 4px;' \
                                            +'background-color: rgb(155, 214, 255)}'
        normalback = 'QLabel{border : transparent;' \
                                    +'border-radius : 4px;' \
                                    + 'background-color :qlineargradient(spread:pad, x1:0.5, y1:0.7, x2:0.5, y2:1,'\
                                    + 'stop:0 rgba(160, 234, 31, 255), stop:1 rgba(127, 183, 23, 247))}'\
                            + 'QGraphicsView{border : transparent;' \
                                            +'border-radius : 4px;' \
                                            + 'background-color :qlineargradient(spread:pad, x1:0.5, y1:0.7, x2:0.5, y2:1,'\
                                            + 'stop:0 rgba(160, 234, 31, 255), stop:1 rgba(127, 183, 23, 247))}'

        abnormalback = 'QLabel{border : transparent;' \
                                    +'border-radius : 4px;'\
                                    +'background-color :qlineargradient(spread:pad, x1:0.5, y1:0.7, x2:0.5, y2:1,'\
                                    +'stop:0 rgba(255, 106, 106, 255), stop:1 rgba(195, 67, 67, 255))}'\
                            +'QGraphicsView{border : transparent;'\
                                            +'border-radius : 4px;'\
                                            +'background-color :qlineargradient(spread:pad, x1:0.5, y1:0.7, x2:0.5, y2:1,'\
                                            +'stop:0 rgba(255, 106, 106, 255), stop:1 rgba(195, 67, 67, 255))}'

        mainButton = 'QPushButton{background-color:rgb(52, 56, 56);'\
                                        +'color : white}'\
                            +'QPushButton:checked{background-color:rgb(0, 145, 255);'\
                                                +'color : white;'\
                                                +'border : 1px solid grey;}'
        abnormaltext= 'QObject{color : red}' 
        normallabel_whitebg = 'QObject{border: 1px solid grey;'\
                                            +'background-color : white;}'
        normallabel_greybg = 'QObject{border: 1px solid grey;'\
                                            +'background-color : rgb(245,245,245)}'
        disalbleButton = 'QPushButton{color : rgb(120,120,120)}'
        lineColor = [(245,183,0),(147,0,250),(0,220,200),(137,252,0)]
        symbolOutlineColor =[(245,183,0),(147,0,250),(0,220,200),(137,252,0)]
        dotLineColor = [(245,183,0,150),(137,252,0,150),(0,161,232,150),(147,0,252,150)]
