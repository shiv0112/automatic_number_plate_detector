import streamlit as st
import os
from PIL import Image
import shutil
import requests
import json
import xmltodict
import glob
import re
import cv2
import easyocr
import imutils

st.title("Automatic License Plate Recogntion")
st.text("\nUpload a video containing a Car with number plate to get License Plate information")

st.write("*"*60)

def upload_video( ):
    uploaded_file = st.file_uploader('Choose a file')

    try:
        dir = './exp/crops'
        shutil.rmtree(dir)
    except:
        pass

    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        
        st.session_state['video_path'] = uploaded_file.name
        st.write('\n\nUploaded video file')
    
        st.video(uploaded_file)

        with open('./loaded/video.mp4', "wb") as vid:
            vid.write(bytes_data)
        start_execution = st.button('Find License Plate')
        if start_execution:
            gif_runner = st.image('./static/loading.gif')
            os.system('python ./yolov5/detect.py --weights ./yolov5/best.pt --img 416 --conf 0.82 --source ./loaded/video.mp4 --save-crop --exist-ok --project ./')
            gif_runner.empty()
        return uploaded_file.name

upload_video()


try:
    image = Image.open('./exp/crops/Number_Plate/video.jpg')
    st.write("*"*60)
    st.markdown("<h1 style='text-align: center;'>Cropped License Plate</h1>", unsafe_allow_html=True)
    st.image(image,width = 700)
    st.write("\n\n")
    p1 = st.markdown("<h3 style='text-align: center;>Retrieving Number from RTO...<h3>", unsafe_allow_html=True)
    gif_runner = st.image('./static/processing.gif')

    image_file_path = './exp/crops/Number_Plate/video.jpg'
    image = cv2.imread(image_file_path)
    
    image = imutils.resize(image, width=300 )
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray_image = cv2.bilateralFilter(gray_image, 11, 17, 17) 
    edged = cv2.Canny(gray_image, 30, 200) 
    cnts,new = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    cnts = sorted(cnts, key = cv2.contourArea, reverse = True) [:30]
    screenCnt = None

    os.makedirs('./final_plate/',exist_ok=True)
    i=7
    for c in cnts:
        perimeter = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.018 * perimeter, True)
        if len(approx) == 4: 
            screenCnt = approx
            x,y,w,h = cv2.boundingRect(c) 
            new_img=image[y:y+h,x:x+w]
            print(x,y,w,h)
            os.chdir('./final_plate/')
            cv2.imwrite(str(i)+'.png',new_img)
            os.chdir('../')
            i+=1
            break

    licensePlate1 = image[y:y+h, x:x + w]
    licensePlate2=image[y:y + h, x+15:x + w]

    if len(os.listdir('./final_plate'))==0:
        os.chdir('./final_plate')
        cv2.imwrite('cropped1.png',licensePlate1)
        cv2.imwrite('cropped2.png',licensePlate2)
        os.chdir("../")
    else:
        files = glob.glob('./fimal_plate')
        for f in files:
                os.remove(f)
        os.chdir('./final_plate')
        cv2.imwrite('cropped1.png',licensePlate1)
        cv2.imwrite('cropped2.png',licensePlate2)
        os.chdir("../")


    reader = easyocr.Reader(['en'])
    img1=os.path.join('./final_plate',"cropped1.png")
    img2=os.path.join('./final_plate',"cropped2.png")


    image1 = cv2.imread(img1)

    img1_res1= reader.readtext(image1)

    image2 = cv2.imread(img2)
    img2_res2= reader.readtext(image2)

    if len(img2_res2)>1:
        res1=str("".join(re.split("[^a-zA-Z0-9]*", img1_res1[1][1]))).upper()
        res2=str("".join(re.split("[^a-zA-Z0-9]*", img2_res2[1][1]))).upper()
        res=[res1,res2]
    else:
        res1=str("".join(re.split("[^a-zA-Z0-9]*", img1_res1[0][1]))).upper()
        res2=str("".join(re.split("[^a-zA-Z0-9]*", img2_res2[0][1]))).upper()
        res=[res1,res2]

    digit2=res[1][-4:]
    to_remove_chars = {"O": "0", "I": "1", "G":"6", "T":"1","S": "6", "Z": "7","4":"A"}
    for char in to_remove_chars.keys():
        digit2 = digit2.replace(char, to_remove_chars[char])


    st1=res[1][:2]
    to_remove_chars = {"1": "I", "5": "S", "6":"G", "7": "Z", "0": "O","4":"A"}
    for char in to_remove_chars.keys():
        st1 = st1.replace(char, to_remove_chars[char])


    digit1=res[1][2:4]
    to_remove_chars = {"I": "1","G":"6", "S": "5", "Z": "7", "O": "0","A":"4"}
    for char in to_remove_chars.keys():
        digit1 = digit1.replace(char, to_remove_chars[char])


    st2=res[1][4:6]
    to_remove_chars = {"1": "I", "6":"G", "5": "S", "7": "Z", "0": "O","4":"A"}
    for char in to_remove_chars.keys():
        st2 = st2.replace(char, to_remove_chars[char])


    vehicle_reg_no=st1+digit1+st2+digit2

    gif_runner.empty()
    p1.empty()
    st.write("*"*60)
    st.markdown("<h1 style='text-align: center;'>"+st1+" "+digit1+" "+st2+" "+digit2+"</h1>", unsafe_allow_html=True)
    st.write("*"*60)
    st.write("\n\n")
    p1 = st.markdown("<h3 style='text-align: center;>Retrieving Number from RTO...<h3>", unsafe_allow_html=True)
    gif_runner = st.image('./static/loading_plate.gif',width = 350)

    vehicle_reg_no = vehicle_reg_no.strip()
    username = "meemo1" #insert your user name
    url = "http://www.regcheck.org.uk/api/reg.asmx/CheckIndia?RegistrationNumber=" + vehicle_reg_no + "&username="+username
    url=url.replace(" ","%20")

    r = requests.get(url)

    n = xmltodict.parse(r.content)
    k = json.dumps(n)
    df = json.loads(k)
    
    l=df["Vehicle"]["vehicleJson"]

    p=json.loads(l)
    
    p1.empty()
    gif_runner.empty()

    st.markdown("<h2 style='text-align: center;'>Detected Car's Details: <h2>", unsafe_allow_html=True)
    st.write("Owner name: "+str(p['Owner']))
    st.write(vehicle_reg_no)
    st.write("Car Company: "+str(p['CarMake']['CurrentTextValue']))
    st.write("Car Model: "+str(p['CarModel']['CurrentTextValue']))
    st.write("Fuel Type: "+str(p['FuelType']['CurrentTextValue']))
    st.write("Registration Year: "+str(p['RegistrationYear']))
    st.write("Insurance: "+str(p['Insurance']))
    st.write("Vehicle ID: "+str(p['VechileIdentificationNumber']))
    st.write("Engine No.: "+str(p['EngineNumber']))
    st.write("Location RTO: "+str(p['Location']))
    

except Exception as e:
    pass


