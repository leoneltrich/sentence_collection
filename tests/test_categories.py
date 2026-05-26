import unittest
import json
from app import create_app
from app.models import db, Category

class TestCategoryRoutes(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_add_category(self):
        response = self.client.post('/categories', 
                                    data=json.dumps({'name': 'Test Cat', 'description': 'Test Desc'}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'Category added successfully')

    def test_update_category(self):
        # First, add a category
        self.client.post('/categories', 
                         data=json.dumps({'name': 'Old Name', 'description': 'Old Desc'}),
                         content_type='application/json')
        
        # Then, update it
        response = self.client.put('/categories/1', 
                                    data=json.dumps({'name': 'New Name', 'description': 'New Desc'}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'Category updated successfully')
        
        # Verify changes in DB
        with self.app.app_context():
            cat = Category.query.get(1)
            self.assertEqual(cat.name, 'New Name')
            self.assertEqual(cat.description, 'New Desc')

    def test_update_category_not_found(self):
        response = self.client.put('/categories/999', 
                                    data=json.dumps({'name': 'New Name'}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 404)

    def test_update_category_duplicate_name(self):
        # Add two categories
        self.client.post('/categories', 
                         data=json.dumps({'name': 'Cat 1'}),
                         content_type='application/json')
        self.client.post('/categories', 
                         data=json.dumps({'name': 'Cat 2'}),
                         content_type='application/json')
        
        # Try to rename Cat 1 to Cat 2
        response = self.client.put('/categories/1', 
                                    data=json.dumps({'name': 'Cat 2'}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 409)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'Category name already exists')

if __name__ == '__main__':
    unittest.main()
