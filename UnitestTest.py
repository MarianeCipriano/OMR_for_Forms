import cv2
import numpy as np
import imutils
from imutils import contours
from imutils.perspective import four_point_transform
from fpdf import FPDF
#from __future__ import print_function
import pyzbar.pyzbar as pyzbar
from OMR import Answers_Card
from OMR import Omr
import OMR
import unittest
from unittest import TestCase


class TestStringMethods(unittest.TestCase):

    def testangle(self):
        img = cv2.imread("gq3.jpeg")
        cap = Answers_Card()
        ali = cap.aling(img)
        #print('Rot',len(ali))
        self.assertEquals(len(ali), 2174)

    def test_barcodes(self):
        img = cv2.imread("test2.png")
        om = Omr(img)
        barc = om.barcodes(img)
        #print(len(barc))
        self.assertEquals(len(barc), 2)

    def test_detect_cir(self):
        img = cv2.imread("gabarito2.png")
        om = Omr(img)
        res = om.DetectQuestions_cir(img)
        self.assertEqual(len(res), 75)
        #print(len(res))
    def test_detect_ret(self):
        img = cv2.imread("HEXAG.jpg")
        om = Omr(img)
        res = om.DetectQuestions_ret(img)
        self.assertEqual(len(res), 305)
        #print(len(res))
    def test_questions(self):
        img = cv2.imread("gabarito2.png")
        dt = Omr(img)
        res = dt.DetectQuestions(img)
        self.assertEqual(len(res), 75)
    def test_sort(self):
        img = cv2.imread('gabarito2.png')
        dt = Omr(img)
        res = dt.sort_contours(img)
        #print(len(res))
        self.assertEqual(len(res), 2)

    def test_findTemplate(self):
        img = cv2.imread("gabarito2.png")
        dt = Omr(img)
        res = dt.Find_Templates(img)
        self.assertEqual(res, 1)

    def test_quantTemplate(self):
        img = cv2.imread("c_resposta.png")
        dt = Omr(img)
        res = dt.Quant_Templates(img)
        self.assertEquals(len(res), 1)
    """
        def test_mark(self):
        img = cv2.imread("gabarito2.png")
        dt = Omr(img)
    """

if __name__ == '__main__':
    unittest.main()