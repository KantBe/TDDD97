const requestTypes = ['GET', 'POST', 'UPDATE', 'DELETE'];

const sendRequest = async (type, url, data) => {
	if (type === 'GET' && data) {
		// write data to url
		url += '?';
		for (const k in data) {
			url += k + '=' + data[k] + '&';
		}
		url = url.substring(0, url.length - 1);
		data = null;
	}

	const request = new XMLHttpRequest();
	const async = true;
	request.open(type, url, async); // true for asynchronous

	request.setRequestHeader('Content-Type', 'application/json');
	request.setRequestHeader('Accept', 'application/json');

	if (data == null) {
		request.send(data);
	} else {
		request.send(JSON.stringify(data));
	}

	return new Promise((resolve, reject) => {
		request.onreadystatechange = () => {
			if (request.readyState == 4) {
				if (request.status / 100 == 2 || request.status / 100 == 3) {
					resolve(JSON.parse(request.responseText));
				} else if (request.status / 100 == 5 || request.status / 100 == 4) {
					reject(JSON.parse(request.responseText));
				}
			}
		};
	});
};

const server = {
	signUp: async (data) => {
		console.log('sign up', data);
		return sendRequest('POST', 'http://127.0.0.1:5000/sign_up/', data)
	},

	signIn: async (email, password) => {
		return sendRequest('GET', 'http://127.0.0.1:5000/sign_in/', {
			username: email,
			password: password,
		});
	},

	signOut: async (token) => {
		console.log('sign out', token);
		return sendRequest('GET', 'http://127.0.0.1:5000/sign_out/', {
			token: token,
		});
	},

	changePassword: (token, oldPassword, newPassword) => {
		console.log('change password', token, oldPassword, newPassword);
	},

	getUserMessagesByEmail: (token, email) => {
		console.log('get user messages by email', token, email);
	},

	postMessage: (token, content, email) => {
		console.log('post message', token, content, email);
	},

	getUserDataByToken: async (token) => {
		console.log('get user data by token', token);
		return sendRequest('GET', 'http://127.0.0.1:5000/get_user_data_by_token/', {
			token: token,
		});
	},

	getUserDataByEmail: async (token, email) => {
		console.log('get user data by email', token, email);
		return sendRequest('GET', 'http://127.0.0.1:5000/get_user_data_by_email/', {
			token: token,
			email: email,
		});
	},
};
