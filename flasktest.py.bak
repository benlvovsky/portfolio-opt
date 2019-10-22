#!/usr/bin/env python
from flask import Flask, Request, request
from StringIO import StringIO
import unittest

RESULT = False

class TestFileFail(unittest.TestCase):

    def test_1(self):

        class FileObj(StringIO):
            
            def close(self):
                print 'in file close'
                global RESULT
                RESULT = True
        
        class MyRequest(Request):
            def _get_file_stream(self, *args, **kwargs):
                return FileObj()

        app = Flask(__name__)
        app.debug = True
        app.request_class = MyRequest

        @app.route("/upload", methods=['POST'])
        def upload():
            f = request.files['file']
            print 'in upload handler'
            self.assertIsInstance(
                f.stream,
                FileObj,
            )
            # Note I've monkeypatched werkzeug.datastructures.FileStorage 
            # so it wont squash exceptions
            f.close()
            #f.stream.close()
            return 'ok'

        client = app.test_client()
        resp = client.post(
            '/upload',
            data = {
                'file': (StringIO('my file contents'), 'hello world.txt'),
            }
        )
        self.assertEqual(
            'ok',
            resp.data,
        )
        global RESULT
        self.assertTrue(RESULT)

    def test_2(self):
        pass
        

if __name__ == '__main__':
    unittest.main()
    
