const requestTypes = ['GET', 'POST', 'UPDATE', 'DELETE'];

const sendGetRequest = (url, data, callback) => {
	const request = new XMLHttpRequest();
	request.onreadystatechange = function () {
		if (request.readyState == 4) {
			callback(JSON.parse(request.responseText));
		}
	};

	// write data to url
	url += '?';
	for (const k in data) {
		url += k + '=' + data[k] + '&';
	}
	url = url.substring(0, url.length - 1);

	const async = true;
	request.open('GET', url, async);
	request.send();
};

const sendRequest = (type, url, data, callback) => {
	if (type === 'GET' && data) {
		sendGetRequest(url, data, callback);
		return;
	}

	const request = new XMLHttpRequest();
	request.onreadystatechange = function () {
		if (request.readyState == 4) {
			console.log(request, request.responseText);
			callback(request.responseText);
		}
	};
	const async = true;
	request.open(type, url, async); // true for asynchronous

	request.setRequestHeader('Content-Type', 'application/json');
	request.setRequestHeader('Accept', 'application/json');

	request.send(data);
};

const server = {
	signUp: (data, callback) => {
		console.log('sign up', data);
	},

	signIn: (email, password, callback) => {
		sendRequest(
			'GET',
			'http://localhost:5000/sign_in/',
			{username: email, password: password},
			callback
		);
	},

	signOut: (token, callback) => {
		console.log('sign out', token);
	},

	changePassword: (token, oldPassword, newPassword, callback) => {
		console.log('change password', token, oldPassword, newPassword);
	},

	getUserMessagesByEmail: (token, email, callback) => {
		console.log('get user messages by email', token, email);
	},

	postMessage: (token, content, email, callback) => {
		console.log('post message', token, content, email);
	},

	getUserDataByToken: (token, callback) => {
		console.log('get user data by token', token);
	},

	getUserDataByEmail: (token, email, callback) => {
		console.log('get user data by email', token, email);
	},
};
