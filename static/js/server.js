const PORT = 443;
const URL = 'tddd97-b11-f93163caa8f5.herokuapp.com';

const API = `https://${URL}`;
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
		return sendRequest('POST', `${API}/sign_up/`, data);
	},

	signIn: async (email, password) => {
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

	postMessage: async (token, content, email) => {
		return sendRequest('POST', `${API}/post_message/`, {
			token: token,
			message: content,
			email: email,
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

	websocket: (token) => {
		if (socket) {
			console.log('socket already exists');
			return;
		}
		socket = new WebSocket(`ws://${URL}/websocket?token=${token}`);
		socket.addEventListener('open', () => {
			socket.send(token);
		});

		socket.addEventListener('message', (event) => {
			const data = event.data;
			if (data === 'logout') {
				localStorage.removeItem('token');
				refresh();

				// and send an information message to the user
				toast.classList.remove('logged-in');
				toastMessage(
					'You were logged out due to another login to your account',
					TOAST_MESSAGE.INFO
				);
			}
		});

		socket.addEventListener('close', (event) => {
			console.log('closing socket', event);
			socket = undefined;
		});
	},
};
