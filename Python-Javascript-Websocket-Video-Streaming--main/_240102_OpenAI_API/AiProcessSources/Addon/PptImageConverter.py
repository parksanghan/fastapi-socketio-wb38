# -*- coding: cp949 -*-

from datetime import datetime

import aspose.slides as slides
import aspose.pydrawing as drawing

def GetNowString() :
    # 현재 시각을 얻음
    current_time = datetime.now()

    # 시간을 원하는 포맷의 문자열로 변환
    formatted_time = current_time.strftime("%Y_%m_%d_%H_%M_%S")
    return formatted_time;


def PptToImage(root : str, tRoot : str) :
    retList : list[str] = []    

    pres = slides.Presentation(root)

    # Loop through slides
    for index in range(pres.slides.length):
        
        # Get reference of slide
        slide = pres.slides[index]
        
        fileName = rf"{tRoot}\image_"+ GetNowString() + "_" + str(index) + ".png"
        
        # Save as JPG
        with slide.get_thumbnail(1, 1) as bitmap : 
            bitmap.save(fileName, drawing.imaging.ImageFormat.png)
        
        retList.append(fileName)

    return retList;







# from datetime import datetime

# from spire.presentation import Presentation

# def GetNowString() :
#     # 현재 시각을 얻음
#     current_time = datetime.now()

#     # 시간을 원하는 포맷의 문자열로 변환
#     formatted_time = current_time.strftime("%Y_%m_%d_%H_%M_%S")
#     return formatted_time;


# def PptToImage(root : str, tRoot : str) :
#     retList : list[str] = []    

#     # Create a Presentation object
#     presentation = Presentation()
    
#     # Load a PowerPoint presentation
#     presentation.LoadFromFile(root)
    
#     # Loop through the slides in the presentation
#     for i, slide in enumerate(presentation.Slides):
        
#         # Specify the output file name
#         fileName = rf"{tRoot}\image_"+ GetNowString() + "_" + str(i) + ".png"
        
#         # Save each slide as a PNG image
#         image = slide.SaveAsImage()
#         image.Save(fileName)
#         image.Dispose()
        
#         retList.append(fileName)

#     presentation.Dispose()
    
#     return retList;

