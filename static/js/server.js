const envs = {0: 'DEV', 1: 'PROD'};
const env = envs[0];

let _PORT, _URL;
if (env === 'PROD') {
	_PORT = 443;
	_URL = 'tddd97-b11-f93163caa8f5.herokuapp.com';
} else {
	_PORT = 5000;
	_URL = '127.0.0.1';
}
const API = `${env === 'PROD' ? 'https' : 'http'}://${_URL}:${_PORT}`;
const requestTypes = ['GET', 'POST', 'UPDATE', 'DELETE'];

let socket;

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
	request.setRequestHeader('Access-Control-Allow-Origin', '*');

	if (data == null) {
		request.send(data);
	} else {
		request.send(JSON.stringify(data));
	}

	return new Promise((resolve, reject) => {
		request.onreadystatechange = () => {
			if (request.readyState == 4) {
				statusType = Math.floor(request.status / 100);
				if (statusType === 2 || statusType === 3) {
					// console.log(JSON.parse(request.responseText), request.status);
					resolve({
						status: request.status,
						response: JSON.parse(request.responseText),
					});
				} else if (statusType === 4 || statusType === 5) {
					// console.error(JSON.parse(request.responseText), request.status);
					reject({
						status: request.status,
						response: JSON.parse(request.responseText),
					});
				}
			}
		};
	});
};

const server = {
	signUp: async (data) => {
		console.log(data);
		return sendRequest('POST', `${API}/sign_up/`, data);
	},

	signIn: async (email, password) => {
		console.log(email, password);
		return sendRequest('GET', `${API}/sign_in/`, {
			username: email,
			password: password,
		});
	},

	signOut: async (token) => {
		return sendRequest('GET', `${API}/sign_out/`, {
			token: token,
		});
	},

	changePassword: async (token, oldPassword, newPassword) => {
		return sendRequest('PUT', `${API}/change_password/`, {
			token: token,
			oldpassword: oldPassword,
			newpassword: newPassword,
		});
	},

	getUserMessagesByEmail: async (token, email) => {
		return sendRequest('GET', `${API}/get_user_messages_by_email/`, {
			token: token,
			email: email,
		});
	},

	postMessage: async (token, content, email, position) => {
		return sendRequest('POST', `${API}/post_message/`, {
			token: token,
			message: content,
			email: email,
			latitude: position.latitude,
			longitude: position.longitude,
		});
	},

	getUserDataByToken: async (token) => {
		return sendRequest('GET', `${API}/get_user_data_by_token/`, {
			token: token,
		});
	},

	getUserDataByEmail: async (token, email) => {
		return sendRequest('GET', `${API}/get_user_data_by_email/`, {
			token: token,
			email: email,
		});
	},

	checkToken: async (token) => {
		return sendRequest('GET', `${API}/check_token`, {
			token: token,
		});
	},

	requestPasswordReset: async (user) => {
		return sendRequest('POST', `${API}/reset_password/`, {
			user,
		});
	},

	setPassword: async (token, password) => {
		return sendRequest('POST', `${API}/set_password/`, {
			token,
			password,
		});
	},

	websocket: (token) => {
		if (socket) {
			console.log('socket already exists');
			return;
		}
		socket = new WebSocket(
			`${env === 'PROD' ? 'wss' : 'ws'}://${_URL}${
				env === 'PROD' ? '' : `:${_PORT}`
			}/websocket?token=${token}`
		);
		socket.addEventListener('open', () => {
			socket.send(token);
		});

		let interval = setInterval(() => {
			if (!socket) {
				clearInterval(interval);
				return;
			}
			socket.send('ping');
		}, 5000);

		socket.addEventListener('message', (event) => {
			const data = event.data;
			// console.log('received data', data);
			if (data === 'logout') {
				// send an information message to the user
				toastElement.classList.remove('logged-in');
				toastMessage(
					'You were logged out due to another login to your account',
					TOAST_MESSAGE.INFO
				);

				localStorage.removeItem('token');
				refresh();
			}
		});

		socket.addEventListener('close', (event) => {
			console.log('closing socket', event);
			clearInterval(interval);

			socket = undefined;
		});
	},
};
