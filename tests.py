import requests
import unittest
import random
import logging
import traceback


class FlaskAppTests(unittest.TestCase):
    logging.basicConfig(level=logging.ERROR)
    base_url = None
    token = None
    user_email = f'MainUser{random.randint(1, 100000000)}@example.com'
    user_email_2 = f'2ndUser{random.randint(1, 100000000)}@example.com'
    random_email = f'test{random.randint(1, 100000000)}@example.com'

    def setUp(self):
        pass

    def tearDown(self):
        # Clean up resources after each test if needed
        pass

    def test_01_sign_up(self):
        url = f'{self.base_url}/sign_up/'
        emails = [self.user_email, self.user_email, self.user_email_2]
        for index, email in enumerate(emails):
            data = {
                'email': email,
                'password': 'password123',
                'firstname': 'John',
                'familyname': 'Doe',
                'gender': 'Male',
                'city': 'Test City',
                'country': 'Test Country'
            }

            try:
                response = requests.post(url, json=data)
                response.raise_for_status()
                result = response.json()
                print(f'test_01_sign_up result: {result}')
                is_positive = contains_true(result)
                if is_positive is None:
                    self.fail(f"Response should contain true or false.")
                if index == 0:
                    self.assertTrue(is_positive, "It looks like the sign up was not successful.")
                    print(f"Test_01_sign_up correct email passed: ✅")
                elif index == 1:
                    self.assertFalse(is_positive, "It looks like the sign up was successful with duplicate email.")
                    print(f"Test_01_sign_up duplicate email passed: ✅")
                else:
                    self.assertTrue(is_positive, "It looks like the sign up was not successful for 2nd user.")
                    print(f"Test_01_sign_up 2nd user passed: ✅")
            except requests.exceptions.HTTPError as e:
                logging.warning(f"HTTPError occurred: {e}")
                print(f"Test_01_sign_up crashed: ❌")
            except requests.exceptions.RequestException as e:
                print(traceback.format_exc())
                self.fail(f"RequestException occurred: {e}")
            except AssertionError as ae:
                # Catching AssertionError and printing a custom failure message
                print(f"Test_01_sign_up failed: ❌ {ae}")

    def test_02_sign_up_invalidate_data(self):
        url = f'{self.base_url}/sign_up/'
        invalid_email = f'invalid{random.randint(1, 100000000)}'
        invalid_emails = [f'{invalid_email}@example', f'{invalid_email}@.com', f'{invalid_email}@exa mple.com']

        for email in invalid_emails:
            data = {
                'email': email,
                'password': 'password123',
                'firstname': 'John',
                'familyname': 'Doe',
                'gender': 'Male',
                'city': 'Test City',
                'country': 'Test Country'
            }

            try:
                response = requests.post(url, json=data)
                response.raise_for_status()
                result = response.json()
                print(f'test_02_sign_up_invalidate_data result: {result}')
                is_positive = contains_true(result)

                if is_positive is None:
                    self.fail(f"Response should contain true or false.")

                self.assertFalse(is_positive, f"It looks like the sign up was successful with invalid email {email}.")
                print(f"test_02_sign_up_invalidate_data passed for invalid email {email}: ✅")
            except requests.exceptions.HTTPError as e:
                logging.warning(f"HTTPError occurred: {e}")
                print(f"test_02_sign_up_invalidate_data crashed for invalid email {email}: ❌")
            except requests.exceptions.RequestException as e:
                self.fail(f"RequestException occurred: {e}")
            except AssertionError as ae:
                print(f"test_02_sign_up_invalidate_data failed for invalid email {email}: ❌ {ae}")

        # List of fields to exclude in each iteration
        fields_to_exclude = ['email', 'password', 'firstname', 'familyname', 'gender', 'city', 'country']
        for field in fields_to_exclude:
            # Create a copy of the data with the current field excluded
            random_email = f'test{random.randint(1, 100000000)}@example.com'
            data = dict(email=random_email, password='password123', firstname='John', familyname='Doe', gender='Male',
                        city='Test City', country='Test Country')
            data[field] = None

            try:
                response = requests.post(url, json=data)
                response.raise_for_status()
                result = response.json()
                print(f'test_02_sign_up_invalidate_data result: {result}')
                is_positive = contains_true(result)

                if is_positive is None:
                    self.fail(f"Response should contain true or false.")

                self.assertFalse(is_positive, f"It looks like the sign up was successful with missing {field}.")
                print(f"test_02_sign_up_invalidate_data passed for missing {field}: ✅")
            except requests.exceptions.HTTPError as e:
                logging.warning(f"HTTPError occurred: {e}")
                print(f"test_02_sign_up_invalidate_data crashed for missing {field}: ❌")
            except requests.exceptions.RequestException as e:
                self.fail(f"RequestException occurred: {e}")
            except AssertionError as ae:
                # Catching AssertionError and printing a custom failure message
                print(f"test_02_sign_up_invalidate_data failed for missing {field}: ❌ {ae}")

    def test_03_sign_in(self):
        url = f'{self.base_url}/sign_in/'
        passwords = ['password123', 'password1234', None]
        for password in passwords:
            data = {
                'username': self.user_email,
                'password': password
            }

            try:
                response = requests.get(url, params=data)
                response.raise_for_status()
                result = response.json()
                print(f'test_03_sign_in result: {result}')
                is_positive = contains_true(result)
                if is_positive is None:
                    self.fail(f"Response should contain true or false.")
                if password == passwords[0]:
                    self.assertTrue(is_positive, "It looks like the sign in was not successful.")
                    headers = response.headers
                    if headers is not None:
                        new_token = headers.get('Authorization')
                        if new_token is not None:
                            FlaskAppTests.token = new_token
                        else:
                            self.fail(f"Token is missing from the response headers.")
                    else:
                        self.fail(f"Response headers are missing.")
                    print(f"test_03_sign_in correct password passed: ✅")
                elif password == passwords[1]:
                    self.assertFalse(is_positive, "It looks like the sign in was successful with incorrect password.")
                    print(f"test_03_sign_in incorrect password passed: ✅")
                else:
                    self.assertFalse(is_positive, "It looks like the sign in was successful with missing password.")
                    print(f"test_03_sign_in missing password passed: ✅")
            except requests.exceptions.HTTPError as e:
                logging.warning(f"HTTPError occurred: {e}")
                print(f"test_03_sign_in crashed: ❌")
            except requests.exceptions.RequestException as e:
                self.fail(f"RequestException occurred: {e}")
            except AssertionError as ae:
                # Catching AssertionError and printing a custom failure message
                print(f"test_03_sign_in failed: ❌ {ae}")

    def test_04_change_password(self):
        url = f'{self.base_url}/change_password/'
        token = self.token
        if token is None:
            self.fail(f"Token is required for change password.")
        combinations_dict_hardcoded = {
            0: {
                "old_passwords": "password123",
                "new_passwords": "password1234",
                "tokens": f'invalid{token}'
            },
            1: {
                "old_passwords": "incorrect_password",
                "new_passwords": "password1234",
                "tokens": token
            },
            2: {
                "old_passwords": "password123",
                "new_passwords": None,
                "tokens": token
            },
            3: {
                "old_passwords": "password123",
                "new_passwords": "password1234",
                "tokens": token
            }
        }
        for i in range(len(combinations_dict_hardcoded)):
            try:
                headers = {'Authorization': combinations_dict_hardcoded[i]["tokens"]}
                response = requests.put(url, json={
                    "oldpassword": combinations_dict_hardcoded[i]["old_passwords"],
                    "newpassword": combinations_dict_hardcoded[i]["new_passwords"]
                }, headers=headers)
                response.raise_for_status()
                result = response.json()
                print(f'test_04_change_password result: {result}')
                is_positive = contains_true(result)
                if is_positive is None:
                    self.fail(f"Response should contain true or false.")
                if i == 0:
                    self.assertFalse(is_positive, "It looks like the change password was successful with "
                                                  "incorrect token.")
                    print(f"test_04_change_password incorrect token passed: ✅")
                elif i == 1:
                    self.assertFalse(is_positive, "It looks like the change password was successful with "
                                                  "incorrect old password.")
                    print(f"test_04_change_password incorrect old password passed: ✅")
                elif i == 2:
                    self.assertFalse(is_positive, "It looks like the change password was successful with "
                                                  "missing new password.")
                    print(f"test_04_change_password missing new password passed: ✅")
                else:
                    self.assertTrue(is_positive, "It looks like the change password was not successful.")
                    print(f"test_04_change_password correct password passed: ✅")
            except requests.exceptions.HTTPError as e:
                logging.warning(f"HTTPError occurred: {e}")
                print(f"test_04_change_password crashed: ❌")
            except requests.exceptions.RequestException as e:
                self.fail(f"RequestException occurred: {e}")
            except AssertionError as ae:
                # Catching AssertionError and printing a custom failure message
                print(f"test_04_change_password failed: ❌ {ae}")

    def test_05_get_user_data_by_token(self):
        url = f'{self.base_url}/get_user_data_by_token/'
        token = self.token
        if token is None:
            self.fail(f"Token is required for get user data by token.")
        tokens = [token, f'{token}123', None]

        for token in tokens:
            try:
                headers = {'Authorization': token}
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                result = response.json()
                print(f'test_05_get_user_data_by_token result: {result}')
                is_positive = contains_true(result)
                if is_positive is None:
                    self.fail(f"Response should contain true or false.")
                if token == tokens[0]:
                    self.assertTrue(is_positive, "It looks like the get user data by token was not successful.")
                    print(f"test_05_get_user_data_by_token correct token passed: ✅")
                elif token == tokens[1]:
                    self.assertFalse(is_positive, "It looks like the get user data by token was successful with "
                                                  "invalid token.")
                    print(f"test_05_get_user_data_by_token incorrect token passed: ✅")
                else:
                    self.assertFalse(is_positive, "It looks like the get user data by token was successful with "
                                                  "missing token.")
                    print(f"test_05_get_user_data_by_token missing token passed: ✅")
            except requests.exceptions.HTTPError as e:
                logging.warning(f"HTTPError occurred: {e}")
                print(f"test_05_get_user_data_by_token crashed: ❌")
            except requests.exceptions.RequestException as e:
                self.fail(f"RequestException occurred: {e}")
            except AssertionError as ae:
                # Catching AssertionError and printing a custom failure message
                print(f"test_05_get_user_data_by_token failed: ❌ {ae}")

    def test_06_get_user_data_by_email(self):
        url = f'{self.base_url}/get_user_data_by_email/'
        token = self.token
        if token is None:
            self.fail(f"Token is required for get user data by email.")
        combination_dict = {
            0: {
                "email": self.user_email,
                "token": token
            },
            1: {
                "email": self.user_email,
                "token": "invalid_token123"
            },
            2: {
                "email": self.user_email,
                "token": None
            },
            3: {
                "email": None,
                "token": token
            },
            4: {
                "email": self.user_email_2,
                "token": token
            },
            5: {
                "email": self.random_email,
                "token": token
            }
        }

        for i in range(len(combination_dict)):
            try:
                headers = {'Authorization': combination_dict[i]["token"]}
                response = requests.get(url, params={
                    "email": combination_dict[i]["email"]
                }, headers=headers)
                response.raise_for_status()
                result = response.json()
                print(f'test_06_get_user_data_by_email result: {result}')
                is_positive = contains_true(result)
                if is_positive is None:
                    self.fail(f"Response should contain true or false.")
                if i == 0:
                    self.assertTrue(is_positive, "It looks like the get user data by email was not successful.")
                    print(f"test_06_get_user_data_by_email correct email passed: ✅")
                elif i == 1:
                    self.assertFalse(is_positive, "It looks like the get user data by email was successful with "
                                                  "invalid token.")
                    print(f"test_06_get_user_data_by_email incorrect token passed: ✅")
                elif i == 2:
                    self.assertFalse(is_positive, "It looks like the get user data by email was successful with "
                                                  "missing token.")
                    print(f"test_06_get_user_data_by_email missing token passed: ✅")
                elif i == 3:
                    self.assertFalse(is_positive, "It looks like the get user data by email was successful with "
                                                  "missing email.")
                    print(f"test_06_get_user_data_by_email missing email passed: ✅")

                elif i == 4:
                    self.assertTrue(is_positive, "It looks like the get 2nd user data by email was not successful.")
                    print(f"test_06_get_user_data_by_email 2nd user passed: ✅")
                else:
                    self.assertFalse(is_positive, "It looks like the get user data by email was successful "
                                                  "with non-existing email.")
                    print(f"test_06_get_user_data_by_email non-existing email passed: ✅")
            except requests.exceptions.HTTPError as e:
                logging.warning(f"HTTPError occurred: {e}")
                print(f"test_06_get_user_data_by_email crashed: ❌")
            except requests.exceptions.RequestException as e:
                self.fail(f"RequestException occurred: {e}")
            except AssertionError as ae:
                # Catching AssertionError and printing a custom failure message
                print(f"test_06_get_user_data_by_email failed: ❌ {ae}")

    def test_07_post_message(self):
        url = f'{self.base_url}/post_message/'
        token = self.token
        if token is None:
            self.fail(f"Token is required for post message.")
        new_input_message = input("Enter a new message: ")
        message_key = input("Enter the message key name in the body (default is 'message'): ") or 'message'
        combinations_dict_hardcoded = {
            0: {
                "message": new_input_message,
                "email": self.user_email,
                "token": f'invalid{token}'
            },
            1: {
                "message": new_input_message,
                "email": self.random_email,
                "token": token
            },
            2: {
                "message": new_input_message,
                "email": self.user_email,
                "token": None
            },
            3: {
                "message": new_input_message,
                "email": None,
                "token": token
            },
            4: {
                "message": None,
                "email": self.user_email,
                "token": token
            },
            5: {
                "message": new_input_message,
                "email": self.user_email_2,
                "token": token
            },
            6: {
                "message": f'Hello, world! {random.randint(1, 1000)}',
                "email": self.user_email,
                "token": token
            },
        }
        for i in range(len(combinations_dict_hardcoded)):
            try:
                headers = {'Authorization': combinations_dict_hardcoded[i]["token"]}
                response = requests.post(url, json={
                    message_key: combinations_dict_hardcoded[i]["message"],
                    "email": combinations_dict_hardcoded[i]["email"]
                }, headers=headers)
                response.raise_for_status()
                result = response.json()
                print(f'test_07_post_message result: {result}')
                is_positive = contains_true(result)
                if is_positive is None:
                    self.fail(f"Response should contain true or false.")
                if i == 0:
                    self.assertFalse(is_positive, "It looks like the post message was successful with "
                                                  "incorrect token.")
                    print(f"test_07_post_message incorrect token passed: ✅")
                elif i == 1:
                    self.assertFalse(is_positive, "It looks like the post message was successful with "
                                                  "non-existing email.")
                    print(f"test_07_post_message non-existing email passed: ✅")
                elif i == 2:
                    self.assertFalse(is_positive, "It looks like the post message was successful with "
                                                  "missing token.")
                    print(f"test_07_post_message missing token passed: ✅")
                elif i == 3:
                    self.assertFalse(is_positive, "It looks like the post message was successful with "
                                                  "missing email.")
                    print(f"test_07_post_message missing email passed: ✅")
                elif i == 4:
                    self.assertFalse(is_positive, "It looks like the post message was successful with "
                                                  "missing message.")
                    print(f"test_07_post_message missing message passed: ✅")
                elif i == 5:
                    self.assertTrue(is_positive, "It looks like the post message was not successful on 2nd user wall.")
                    print(f"test_07_post_message 2nd user post on wall passed: ✅")
                else:
                    self.assertTrue(is_positive, "It looks like the post message was not successful on main user wall.")
                    print(f"test_07_post_message main user post on wall passed: ✅")
            except requests.exceptions.HTTPError as e:
                logging.warning(f"HTTPError occurred: {e}")
                print(f"test_07_post_message crashed: ❌")
            except requests.exceptions.RequestException as e:
                self.fail(f"RequestException occurred: {e}")
            except AssertionError as ae:
                # Catching AssertionError and printing a custom failure message
                print(f"test_07_post_message failed: ❌ {ae}")

    def test_08_get_user_messages_by_token(self):
        url = f'{self.base_url}/get_user_messages_by_token/'
        token = self.token
        if token is None:
            self.fail(f"Token is required for get user messages by token.")
        tokens = [token, f'{token}123', None]

        for token in tokens:
            try:
                headers = {'Authorization': token}
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                result = response.json()
                print(f'test_08_get_user_messages_by_token result: {result}')
                is_positive = contains_true(result)
                if is_positive is None:
                    self.fail(f"Response should contain true or false.")
                if token == tokens[0]:
                    self.assertTrue(is_positive, "It looks like the get user messages by token was not successful.")
                    print(f"test_08_get_user_messages_by_token correct token passed: ✅")
                elif token == tokens[1]:
                    self.assertFalse(is_positive, "It looks like the get user messages by token was successful with "
                                                  "invalid token.")
                    print(f"test_08_get_user_messages_by_token incorrect token passed: ✅")
                else:
                    self.assertFalse(is_positive, "It looks like the get user messages by token was successful with "
                                                  "missing token.")
                    print(f"test_08_get_user_messages_by_token missing token passed: ✅")
            except requests.exceptions.HTTPError as e:
                logging.warning(f"HTTPError occurred: {e}")
                print(f"test_08_get_user_messages_by_token crashed: ❌")
            except requests.exceptions.RequestException as e:
                self.fail(f"RequestException occurred: {e}")
            except AssertionError as ae:
                # Catching AssertionError and printing a custom failure message
                print(f"test_08_get_user_messages_by_token failed: ❌ {ae}")

    def test_09_get_user_messages_by_email(self):
        url = f'{self.base_url}/get_user_messages_by_email/'
        token = self.token
        if token is None:
            self.fail(f"Token is required for get user messages by email.")
        combination_dict = {
            0: {
                "email": self.user_email,
                "token": token
            },
            1: {
                "email": self.user_email,
                "token": "invalid_token123"
            },
            2: {
                "email": self.user_email,
                "token": None
            },
            3: {
                "email": None,
                "token": token
            },
            4: {
                "email": self.user_email_2,
                "token": token
            },
            5: {
                "email": self.random_email,
                "token": token
            }
        }

        for i in range(len(combination_dict)):
            try:
                headers = {'Authorization': combination_dict[i]["token"]}
                response = requests.get(url, params={
                    "email": combination_dict[i]["email"]
                }, headers=headers)
                response.raise_for_status()
                result = response.json()
                print(f'test_09_get_user_messages_by_email result: {result}')
                is_positive = contains_true(result)
                if is_positive is None:
                    self.fail(f"Response should contain true or false.")
                if i == 0:
                    self.assertTrue(is_positive, "It looks like the get user messages by email was not successful.")
                    print(f"test_09_get_user_messages_by_email correct email passed: ✅")
                elif i == 1:
                    self.assertFalse(is_positive, "It looks like the get user messages by email was successful with "
                                                  "invalid token.")
                    print(f"test_09_get_user_messages_by_email incorrect token passed: ✅")
                elif i == 2:
                    self.assertFalse(is_positive, "It looks like the get user messages by email was successful with "
                                                  "missing token.")
                    print(f"test_09_get_user_messages_by_email missing token passed: ✅")
                elif i == 3:
                    self.assertFalse(is_positive, "It looks like the get user messages by email was successful with "
                                                  "missing email.")
                    print(f"test_09_get_user_messages_by_email missing email passed: ✅")

                elif i == 4:
                    self.assertTrue(is_positive, "It looks like the get 2nd user messages by email was not successful.")
                    print(f"test_09_get_user_messages_by_email 2nd user passed: ✅")
                else:
                    self.assertFalse(is_positive, "It looks like the get user messages by email was successful "
                                                  "with non-existing email.")
                    print(f"test_09_get_user_messages_by_email non-existing email passed: ✅")
            except requests.exceptions.HTTPError as e:
                logging.warning(f"HTTPError occurred: {e}")
                print(f"test_09_get_user_messages_by_email crashed: ❌")
            except requests.exceptions.RequestException as e:
                self.fail(f"RequestException occurred: {e}")
            except AssertionError as ae:
                # Catching AssertionError and printing a custom failure message
                print(f"test_09_get_user_messages_by_email failed: ❌ {ae}")

    def test_10_sign_out(self):
        url = f'{self.base_url}/sign_out/'
        token = self.token
        if token is None:
            self.fail(f"Token is required for sign out.")
        tokens = [token, f'{token}123', None]

        for token in tokens:
            try:
                headers = {'Authorization': token}
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                result = response.json()
                print(f'test_10_sign_out result: {result}')
                is_positive = contains_true(result)
                if is_positive is None:
                    self.fail(f"Response should contain true or false.")
                if token == tokens[0]:
                    self.assertTrue(is_positive, "It looks like the sign out was not successful.")
                    print(f"test_10_sign_out correct token passed: ✅")
                elif token == tokens[1]:
                    self.assertFalse(is_positive, "It looks like the sign out was successful with invalid token.")
                    print(f"test_10_sign_out incorrect token passed: ✅")
                else:
                    self.assertFalse(is_positive, "It looks like the sign out was successful with missing token.")
                    print(f"test_10_sign_out missing token passed: ✅")
            except requests.exceptions.HTTPError as e:
                logging.warning(f"HTTPError occurred: {e}")
                print(f"test_10_sign_out crashed: ❌")
            except requests.exceptions.RequestException as e:
                self.fail(f"RequestException occurred: {e}")
            except AssertionError as ae:
                # Catching AssertionError and printing a custom failure message
                print(f"test_10_sign_out failed: ❌ {ae}")


def contains_true(json_data):
    if isinstance(json_data, dict):
        for value in json_data.values():
            result = contains_true(value)
            if result is not None:
                return result
    elif isinstance(json_data, list):
        for item in json_data:
            result = contains_true(item)
            if result is not None:
                return result
    elif isinstance(json_data, str):
        if json_data.lower() == "true":
            return True
        elif json_data.lower() == "false":
            return False
    elif json_data is True:
        return True
    elif json_data is False:
        return False

    return None


def get_token_value(json_data, target_token):
    if isinstance(json_data, dict):
        for key, value in json_data.items():
            if key == target_token:
                return value
            result = get_token_value(value, target_token)
            if result is not None:
                return result
    elif isinstance(json_data, list):
        for item in json_data:
            result = get_token_value(item, target_token)
            if result is not None:
                return result

    return None


def set_up_base_url():
    default_address = 'http://127.0.0.1'
    default_port = 5000

    address = input(f'Enter address (default {default_address}): ') or default_address
    port = input(f'Enter port (default {default_port}): ') or default_port

    return f'{address}:{port}'


if __name__ == '__main__':
    FlaskAppTests.base_url = set_up_base_url()
    unittest.main()
