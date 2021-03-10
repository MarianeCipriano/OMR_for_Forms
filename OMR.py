import cv2
import numpy as np
import os
import imutils
from imutils import contours
from imutils.perspective import four_point_transform
import pyzbar.pyzbar as pyzbar
import json

class Answers_Card:
    dict2 = {}
    obj = None
    def __init__(self):
        self.angle = 0
        self.coords = 0
        self.rotated =0
        self.file = None
    def correctangle(self, img):
        self.gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        self.gray = cv2.bitwise_not(self.gray)

        self.thresh = cv2.threshold(self.gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

        coords = np.column_stack(np.where(self.thresh > 0))
        self.angle = cv2.minAreaRect(coords)[-1]

        if self.angle < -45:
            self.angle = -(90 + self.angle)
        else:
            self.angle = -self.angle
        (h, w) = img.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, self.angle, 1.0)
        self.rotated = cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        print("Angle: {:.2f}".format(self.angle))
        return self.rotated

    def detectQRCodeCodBarras(self, img):
        # Find barcodes and QR codes
        self.file = open('datas.txt', 'w+')
        img = self.correctangle(img)
        decodedObjects = pyzbar.decode(img)
        print(len(decodedObjects))
        for self.obj in decodedObjects:
            self.file.write("{} {}\n".format(self.obj.type, self.obj.data))
            print("{} {}".format(self.obj.type, self.obj.data))
            (x, y, w, h) = self.obj.rect
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)
        if self.obj is None:
            self.file.write("Barcodes NotExist")
        self.file = "datas.txt"
        self.dict2 = {}
        with open(self.file) as fh:
            for line in fh:
                command, description = line.strip().split(None, 1)

                self.dict2[command] = description.strip()
        print('dict2', self.dict2)
            #cv2.imshow("Input", img)
        return decodedObjects

class Omr:
    description = None
    json_res = None
    barcodes = None
    Rows = 0
    Cols = 0
    ansewrs = 0
    paper_objs = None
    gab = 0
    rows = 0
    questionsCnts = 0
    totQuestions = 0
    id = 0
    obj = None
    dict = {}
    dict1 = {}
    paper = None
    ques = []
    def __init__(self, img):
        self.questions = []
        self.questions1 = []
        self.questions2 = []
        self.res = []
        self.bubbled = None
        self.paper = None
        self.cont = 0
        self.alt = 0
        self.num_col = 0
        self.cols = 0
        #self.obj = None
        self.rectCont = None
        self.file = None

    def pre_process(self, img):
        img = cap.correctangle(img)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        self.thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
        self.cnts, hier = cv2.findContours(self.thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        #self.cnts = imutils.grab_contours(self.cnts)

    def sort_contours(self, cnts, method="left-to-right"):
        reverse = False
        i = 0
        if method == "right-to-left" or method == "bottom-to-top":
            reverse = True

        if method == "top-to-bottom" or method == "bottom-to-top":
            i = 1

        self.boundingBoxes = [cv2.boundingRect(c) for c in cnts]

        (self.cnts, self.boundingBoxes) = zip(
            *sorted(zip(cnts, self.boundingBoxes), key=lambda b: b[1][i], reverse=reverse))

        return (self.cnts, self.boundingBoxes)

    def DetectQuestions_cir_quad(self, img):
        p1 = self.pre_process(img)
        sc = self.sort_contours(self.cnts, method="left-to-rigth")
        (self.cnts, self.boundingBoxes) = self.sort_contours(self.cnts, method=["method"])
        for c in self.cnts:
            (x, y, w, h) = cv2.boundingRect(c)
            ar = w / float(h)
            if (w >= 10 and h >= 10 and ar >= 0.9 and ar <= 1.1):
                self.questions1.append(c)
                cv2.drawContours(img, self.questions1, -1, (0,0,255), 1)
        #print(len(self.questions1))
        if len(self.questions1) > 40:
            self.questions = self.questions1
            print('quant.alter: ', len(self.questions))
        return self.questions1

    def DetectQuestions_ret(self, img):
        p1 = self.pre_process(img)
        sc = self.sort_contours(self.cnts, method="left-to-rigth")
        (self.cnts, self.boundingBoxes) = self.sort_contours(self.cnts, method=["method"])
        for c in self.cnts:
            (x, y, w, h) = cv2.boundingRect(c)
            ar = w / float(h)
            if  w > 10 and h < 10:
                self.questions2.append(c)
                cv2.drawContours(img, self.questions2, -1, (0, 0, 255), 1)
        #print(len(self.questions2))
        if len(self.questions2) > 40:
            self.questions = self.questions2
            print('quant.alter: ', len(self.questions))
        return self.questions2
    """  
     def DetectQuestions(self, img):
        dt = self.DetectQuestions_cir_quad(img)

        if len(self.questions1) > 40:
            self.questions = self.questions1
        elif len(self.questions2) > 40:
            dt = self.DetectQuestions_ret(img)
            self.questions = self.questions2
        print('quant.alter: ', len(self.questions))
        cv2.drawContours(img, self.questions, -1, (0, 0, 255), 1)
        #self.questions = contours.sort_contours(self.questions, method="top-to-bottom")[0]
        return self.questions
    """

    def Hor_Ver(self, img):
        self.v_h = input("Type h for horizontal or v for vertical: ")
        if (self.v_h == "h" or self.v_h == "H"):
            self.questions = contours.sort_contours(self.questions, method="top-to-bottom")[0]
        elif (self.v_h == "v" or self.v_h == "V"):
            self.questions = contours.sort_contours(self.questions, method="left-to-right")[0]
        else:
            self.questions = contours.sort_contours(self.questions, method="top-to-bottom")[0]
        return self.questions


    def detectMark(self, img):
        self.file = open('data.txt', 'w+')
        #dt = self.DetectQuestions(img)
        self.questions = contours.sort_contours(self.questions, method="top-to-bottom")[0]
        res = []
        bubbled = None
        self.alt = int(input('Number of alternatives per question: '))
        self.num_col = int(input('Number of gabarito columns: '))
        for (q, i) in enumerate(np.arange(0, len(self.questions), self.alt)):
            self.cont = 0
            cnts = contours.sort_contours(self.questions[i:i + self.alt])[0]
            self.questionsCnts += 1
            for (j, c) in enumerate(cnts):
                mask = np.zeros(self.thresh.shape, dtype="uint8")
                cv2.drawContours(mask, [c], -1, (255, 255, 255), -1)
                mask = cv2.bitwise_and(self.thresh, self.thresh, mask=mask)
                numPixels = cv2.countNonZero(mask)
                # print('pixel de cada questao:',numPixels)
                if numPixels >= len(self.thresh) * 0.7:
                    # print('MARK', cont)
                    res.append(c)
                    self.cont += 1
                    bubbled = (numPixels, j)
                    cv2.drawContours(img, res, -1, (0, 255, 0), 2)
                    if self.cont == 1:
                        if j == 0:
                            j = 'A'
                        if j == 1:
                            j = 'B'
                        if j == 2:
                            j = 'C'
                        if j == 3:
                            j = 'D'
                        if j == 4:
                            j = 'E'
                        self.id = j
            if self.cont > 2:
                self.id = 'nulo'
            elif self.cont == 0:
                self.id = 'white'
            #f.write('{} {}\n'.format(self.questionsCnts, self.id))
            #print('Questao', self.questionsCnts, ':', self.id)
            self.file.write('{}: {}\n'.format(self.questionsCnts, self.id))
        self.file = "data.txt"
        self.dict1 = {}
        with open(self.file) as fh:
            for line in fh:
                command, description = line.strip().split(None, 1)

                self.dict1[command] = description.strip()
        self.totalQuestions = self.questionsCnts
        self.Rows = int(self.questionsCnts / self.num_col)
        self.Cols = int(self.alt * (self.num_col*self.gab))
        self.dict = {
            "Gab": self.gab, #num gabaritos
            "Number Cols": self.num_col,
            "Rows": self.Rows,
            "Cols": self.Cols,
            "Questions": self.totQuestions,
            "Mark": self.dict1 #questoes e respostas
        }
        print('Modelo', self.dict)
        return self.dict

    def Quant_Templates(self, img):
        #img = cap.aling(img)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edged = cv2.Canny(blurred, 75, 200)
        cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2:]
        cnts = imutils.grab_contours(cnts)
        cnts = contours.sort_contours(cnts, method="top-to-bottom")[0]
        self.rectCon = None
        self.ques = []
        for (i, c) in enumerate(cnts):
            x, y, w, h = cv2.boundingRect(c)
            approx = cv2.approxPolyDP(c, 0.01 * cv2.arcLength(c, True), True)
            if len(approx) == 4 and w * h > 1000:
                #ques.append(c)
		        #print(len(self.ques))
                self.rectCont = approx.reshape(4,2)
                paper = four_point_transform(img, self.rectCont)
                cv2.imshow('OK', paper)
                cv2.waitKey(0)
                dt = self.DetectQuestions_cir_quad(paper)
                cv2.drawContours(img, [self.rectCont], -1, (255, 0, 0), 2)
                cv2.drawContours(paper, self.questions, -1, (255, 0, 0), 2)
                if ((len(self.questions))) >= 5:
                    self.gab += 1
                    dt = self.detectMark(img)
                    self.ques.append(dt)
                    print('Ques',self.ques)
                else:
                    self.gab = 0
                    print('não há gabaritos')
        return self.gab

    def Find_Templates(self, img):
        img = cap.correctangle(img)
        self.ques = []
        dt = self.DetectQuestions_cir_quad(img)
        #print(len(self.questions))
        if len(self.questions) > 50:
            self.gab += 1
            dt = self.detectMark(img)
            self.ques.append(dt)
            lista = "Template {}\n".format(self.gab)
            #f.write("Template {}: Alter {}\n".format(self.gab, len(self.questions)))
        else:
            dt = self.Quant_Templates(img)
            if self.gab == 0:
                dt = self.DetectQuestions_ret(img)
                if len(self.questions) > 50:
                    self.gab += 1
                    dt = self.detectMark(img)
                    self.ques.append(dt)
                else:
                    dt = self.Quant_Templates(img)
        return self.gab

    def dump_data(self, img):
        dict_data = {
            "Barcodes ": cap.detectQRCodeCodBarras(img),
            "Total Rows": self.Rows,
            "Total Cols": self.Cols,
            "Amount of templates": self.gab,
            "Templates": self.ques
        }

        with open('dados1.json', 'w', encoding='utf-8') as f:
            json.dump(dict_data, f, ensure_ascii=False, indent=4)
        with open('dados1.json') as data_file:
            data_loaded = json.load(data_file)
        print(dict_data == data_loaded)
        return json.dumps(dict_data)

if __name__ == '__main__':

    img = cv2.imread('gabarito2.png', cv2.IMREAD_UNCHANGED)
    cap = Answers_Card()
    ali = cap.correctangle(img)
    dt = Omr(img)
    cap.detectQRCodeCodBarras(img)
    dt.Find_Templates(img)
    dt.dump_data(img)
    cv2.waitKey(0)


