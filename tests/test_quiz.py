import unittest
import json
import hashlib
from app import create_app
from app.models import db, QuizResult

class TestQuizRoutes(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        # Disable rate limiting in tests so they run fine
        self.app.config['RATELIMIT_ENABLED'] = False
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_quiz_page_served_at_root(self):
        # The standard route / should render the quiz
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Are you a CLI Novice or Expert?', response.data)

    def test_submit_quiz_success(self):
        email = "test@example.com"
        hashed_email = hashlib.sha256(email.encode('utf-8')).hexdigest()
        
        response = self.client.post('/quiz/submit',
                                    data=json.dumps({
                                        'email': email,
                                        'score': 8,
                                        'total': 10,
                                        'level': 'expert'
                                    }),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'Quiz results saved. Thank you for participating!')
        
        # Verify in DB
        with self.app.app_context():
            result = QuizResult.query.filter_by(email=hashed_email).first()
            self.assertIsNotNone(result)
            self.assertEqual(result.score, 8)
            self.assertEqual(result.level, 'expert')
            
            # Verify cleartext email is NOT stored in DB
            result_by_cleartext = QuizResult.query.filter_by(email=email).first()
            self.assertIsNone(result_by_cleartext)

    def test_submit_quiz_duplicate_email(self):
        email = "duplicate@example.com"
        
        # First submission
        response1 = self.client.post('/quiz/submit',
                                     data=json.dumps({
                                         'email': email,
                                         'score': 5,
                                         'total': 10,
                                         'level': 'intermediate'
                                     }),
                                     content_type='application/json')
        self.assertEqual(response1.status_code, 201)
        
        # Second submission with same email
        response2 = self.client.post('/quiz/submit',
                                     data=json.dumps({
                                         'email': email,
                                         'score': 6,
                                         'total': 10,
                                         'level': 'intermediate'
                                     }),
                                     content_type='application/json')
        self.assertEqual(response2.status_code, 400)
        data2 = json.loads(response2.data)
        self.assertIn('already been used', data2['error'])

    def test_submit_quiz_missing_fields(self):
        # Missing email
        response = self.client.post('/quiz/submit',
                                    data=json.dumps({
                                        'score': 8,
                                        'level': 'expert'
                                    }),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 400)

        # Missing score
        response = self.client.post('/quiz/submit',
                                    data=json.dumps({
                                        'email': 'test@example.com',
                                        'level': 'expert'
                                    }),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_submit_quiz_invalid_email(self):
        response = self.client.post('/quiz/submit',
                                    data=json.dumps({
                                        'email': 'invalidemail',
                                        'score': 8,
                                        'level': 'expert'
                                    }),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'Invalid email address')

if __name__ == '__main__':
    unittest.main()
