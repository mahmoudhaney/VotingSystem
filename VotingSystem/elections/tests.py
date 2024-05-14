from rest_framework.test import APITestCase 
from django.urls import reverse
from users.tests import create_admin_user, authenticate_user, generate_test_image, create_basic_user
from rest_framework import status
from .models import Election

def create_list_election_url():
    return reverse('elections:elections-list-create')

def create_candidate_url():
    return reverse('users:candidate_create')

def HTTP_AUTHORIZATION_HEADER(token):
    return {'HTTP_AUTHORIZATION': f'Bearer {token}'}

def election_data():
    return {
        'name': 'Test Election 2024',
        'description': 'Test Description',
        'start_date': '2024-04-26T00:00:00Z',
        'end_date': '2024-04-28T00:00:00Z',
    }

def candidate_data(election_uuid=None):
    return {
        'name': 'Test Candidate',
        'bio': 'Test Bio',
        'photo': generate_test_image(),
        'election_uuid': election_uuid,
    }

def create_election(instance, url, data, headers):
    response = instance.client.post(url, data, **headers)
    return response

class ElectionListCreateViewTestCase(APITestCase):
    def setUp(self):
        self.url = create_list_election_url()
        self.admin_user = create_admin_user()
        self.refresh_token, self.access_token = authenticate_user(self.admin_user)
        self.headers = HTTP_AUTHORIZATION_HEADER(self.access_token)
        self.data = election_data()

    def test_create_election_success(self):
        response = create_election(self, self.url, self.data, self.headers)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('name', response.data)
        self.assertIn('description', response.data)
        self.assertIn('start_date', response.data)
        self.assertIn('end_date', response.data)
        self.assertIn('uuid', response.data)

    def test_create_election_invalid_data(self):
        invalid_data = {
            'name': 'Test ;Election 202',
            'description': 'Test Description%',
            'start_date': '2-04-26T00:00:00Z',
            'end_date': '1990-04-28T00:00:00Z',
        }
        response = self.client.post(self.url, invalid_data, **self.headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)
        self.assertIn('description', response.data)
        self.assertIn('start_date', response.data)

    def test_create_election_with_missing_data(self):
        response = self.client.post(self.url, {}, **self.headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)
        self.assertIn('start_date', response.data)
        self.assertIn('end_date', response.data)

    def test_create_election_without_authentication(self):
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_election_with_wrong_authentication(self):
        self.headers = {'HTTP_AUTHORIZATION': f'Bearer wrong_token_here'}
        response = self.client.post(self.url, self.data, **self.headers)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_election_with_inactive_user(self):
        self.admin_user.is_active = False
        self.admin_user.save()
        response = self.client.post(self.url, self.data, **self.headers)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_election_with_invalid_description(self):
        self.data['description'] = 'Test Description%'
        response = self.client.post(self.url, self.data, **self.headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('description', response.data)

    def test_create_election_with_invalid_date_range(self):
        self.data['start_date'] = '2024-04-26T00:00:00Z'
        self.data['end_date'] = '2024-04-26T00:00:00Z'
        response = self.client.post(self.url, self.data, **self.headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)

    def test_create_election_with_invalid_date_difference(self):
        self.data['end_date'] = '2024-04-27T00:00:00Z'
        response = self.client.post(self.url, self.data, **self.headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)

    def test_create_election_with_invalid_date_year(self):
        self.data['start_date'] = '2023-04-26T00:00:00Z'
        self.data['end_date'] = '2023-04-28T00:00:00Z'
        response = self.client.post(self.url, self.data, **self.headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)

    def test_list_ended_elections(self):
        response = self.client.post(self.url, self.data, **self.headers)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Deactivate the election by setting is_active to False
        election = Election.objects.get(uuid=response.data['uuid']  )
        election.is_active = False
        election.save()

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

class ElectionCandidatesViewTestCase(APITestCase):
    def setUp(self):
        self.url = reverse('elections:elections-list-create')
        self.admin_user = create_admin_user()
        self.refresh_token, self.access_token = authenticate_user(self.admin_user)
        self.headers = HTTP_AUTHORIZATION_HEADER(self.access_token)
        self.election_data = election_data()

    def test_get_election_candidates_success(self):
        election_response = create_election(self, create_list_election_url(), self.election_data, self.headers)
        election_uuid = election_response.data['uuid']

        candidate_url = create_candidate_url()
        self.client.post(candidate_url, candidate_data(election_uuid), format='multipart', **self.headers)
        self.client.post(candidate_url, candidate_data(election_uuid), format='multipart', **self.headers)
        self.client.post(candidate_url, candidate_data(election_uuid), format='multipart', **self.headers)

        response = self.client.get(f'{self.url}{election_response.data["uuid"]}/candidates/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_get_election_candidates_with_invalid_election_uuid(self):
        response = self.client.get(f'{self.url}invalid_uuid/candidates/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_election_candidates_with_no_candidates(self):
        election_response = create_election(self, create_list_election_url(), self.election_data, self.headers)
        response = self.client.get(f'{self.url}{election_response.data["uuid"]}/candidates/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

class VoteCreateViewTestCase(APITestCase):
    def setUp(self):
        # Create elections
        self.admin_user = create_admin_user()
        refresh_token, access_token = authenticate_user(self.admin_user)
        headers = {'HTTP_AUTHORIZATION': f'Bearer {access_token}'}
        election_data = {
        'name': 'Test Election 2024',
        'description': 'Test Description',
        'start_date': '2024-04-26T00:00:00Z',
        'end_date': '2024-04-28T00:00:00Z',
        }
        self.election1_response = self.client.post(reverse('elections:elections-list-create'), election_data, **headers)
        self.election1_uuid = self.election1_response.data['uuid']
        self.election2_response = self.client.post(reverse('elections:elections-list-create'), election_data, **headers)
        self.election2_uuid = self.election2_response.data['uuid']

        # Create a candidates
        self.image_file = generate_test_image()
        candidate_data = {
            'name': 'Test Candidate One',
            'bio': 'Test Bio',
            'photo': self.image_file,
            'election_uuid': self.election1_uuid
        }
        self.candidate1_response = self.client.post(reverse('users:candidate_create'), candidate_data, **headers)
        self.candidate1_uuid = self.candidate1_response.data['uuid']

        candidate_data['name'] = 'Test Candidate Two'
        candidate_data['photo'] = generate_test_image()
        candidate_data['election_uuid'] = self.election2_uuid
        self.candidate2_response = self.client.post(reverse('users:candidate_create'), candidate_data, **headers)
        self.candidate2_uuid = self.candidate2_response.data['uuid']

        self.url = reverse('elections:vote')
        self.user = create_basic_user()
        self.refresh_token, self.access_token = authenticate_user(self.user)
        self.headers = HTTP_AUTHORIZATION_HEADER(self.access_token)
        self.data = {
            'election_uuid': self.election1_uuid,
            'candidate_uuid': self.candidate1_uuid,
        }

    def test_create_vote_success(self):
        response = self.client.post(self.url, self.data, **self.headers)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('election_uuid', response.data)
        self.assertIn('candidate_uuid', response.data)

    def test_create_vote_with_missing_data(self):
        response = self.client.post(self.url, {}, **self.headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('election_uuid', response.data)
        self.assertIn('candidate_uuid', response.data)

    def test_create_vote_candidate_not_in_election(self):
        self.data['candidate_uuid'] = self.candidate2_uuid
        response = self.client.post(self.url, self.data, **self.headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('candidate', response.data)
        self.assertEqual(response.data['candidate'][0], 'This candidate not found for this election.')

    def test_create_vote_with_invalid_election_uuid(self):
        self.data['election_uuid'] = 'invalid_uuid'
        response = self.client.post(self.url, self.data, **self.headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('election_uuid', response.data)

    def test_create_vote_with_invalid_candidate_uuid(self):
        self.data['candidate_uuid'] = 'invalid_uuid'
        response = self.client.post(self.url, self.data, **self.headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('candidate_uuid', response.data)

    def test_create_vote_election_not_found(self):
        self.data['election_uuid'] = '00000000-0000-0000-0000-000000000000'
        response = self.client.post(self.url, self.data, **self.headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_vote_candidate_not_found(self):
        self.data['candidate_uuid'] = '00000000-0000-0000-0000-000000000000'
        response = self.client.post(self.url, self.data, **self.headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_vote_with_invalid_election(self):
        # Deactivate the election by setting is_active to False
        election = Election.objects.get(uuid=self.election1_uuid)
        election.is_active = False
        election.save()
        # Attempt to vote in the election
        response = self.client.post(self.url, self.data, **self.headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('election_uuid', response.data)

    def test_create_vote_with_existing_vote(self):
        self.client.post(self.url, self.data, **self.headers)
        response = self.client.post(self.url, self.data, **self.headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('voter', response.data)

    def test_create_vote_without_authentication(self):
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_vote_with_wrong_authentication(self):
        headers = {'HTTP_AUTHORIZATION': f'Bearer wrong_token_here'}
        response = self.client.post(self.url, self.data, **headers)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_vote_with_inactive_user(self):
        self.user.is_active = False
        self.user.save()
        response = self.client.post(self.url, self.data, **self.headers)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
