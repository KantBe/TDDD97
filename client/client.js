const MIN_LENGTH_PASSWORD = 8;
const PROFILE_TABS = ['home', 'browse', 'account'];
let toast;

getToken = function () {
	return localStorage.getItem('token');
};

displayView = function (id) {
	// the code required to display a view
	const view = document.getElementById(id);
	document.getElementById('content').innerHTML = view.innerHTML;
};

refresh = function () {
	toast = document.getElementById('toast');
	toast.classList = [];

	document.getElementById('content').innerHTML = '';
	const token = getToken();
	const users = JSON.parse(localStorage.getItem('loggedinusers'));
	if (token && users && users[token]) {
		// logged in
		displayView('profileView');
		toast.classList.add('logged-in');

		clearHistory();
		clearSearchResults();
		updateProfileInformation(token);

		document.password_reset.addEventListener('submit', (e) => {
			e.preventDefault();
			changePassword();
		});
		document.search.addEventListener('submit', (e) => {
			e.preventDefault();
			searchUser(token);
		});
		document.post.addEventListener('submit', (e) => {
			e.preventDefault();
			postMessage(token);
		});
	} else {
		// not logged in
		if (token) {
			localStorage.removeItem('token');
		}
		if (users) {
			localStorage.setItem('loggedinusers', '{}');
		}

		displayView('welcomeView');

		document.signup.addEventListener('submit', (e) => {
			e.preventDefault();
			signup();
		});
		document.login.addEventListener('submit', (e) => {
			e.preventDefault();
			login(document.login.email.value, document.login.password.value);
		});
	}
};

window.onload = function () {
	refresh();
};

signup = function () {
	const form = document.signup;
	if (!checkPassword(form)) {
		return;
	}

	const data = {
		email: form.email.value,
		password: form.password.value,
		firstname: form.firstname.value,
		familyname: form.lastname.value,
		gender: form.gender.value,
		city: form.city.value,
		country: form.country.value,
	};

	const res = serverstub.signUp(data);
	if (res.success) {
		toastMessage(res.message, TOAST_MESSAGE.SUCCESS);
		login(data.email, data.password);
	} else {
		toastMessage(res.message, TOAST_MESSAGE.ERROR);
		console.error('error signing up user', res.message);
	}
};

login = function (email, password) {
	const res = serverstub.signIn(email, password);
	if (res.success) {
		localStorage.setItem('token', res.data);
		refresh();
		toastMessage(res.message, TOAST_MESSAGE.SUCCESS);
	} else {
		toastMessage(res.message, TOAST_MESSAGE.ERROR);
	}
};

logout = function () {
	const token = getToken();
	const res = serverstub.signOut(token);
	// console.log(res);
	if (res.success) {
		localStorage.removeItem('token');
	}
	refresh();
	toast.classList.remove('logged-in');
	toastMessage(res.message, TOAST_MESSAGE.SUCCESS);
};

changePassword = function () {
	const form = document.password_reset;
	if (form.password_new.value.length < MIN_LENGTH_PASSWORD) {
		invalid(
			form.password_new,
			`Password must be at least ${MIN_LENGTH_PASSWORD} characters long!`
		);
		return;
	}

	const response = serverstub.changePassword(
		getToken(),
		form.password_old.value,
		form.password_new.value
	);

	// console.log('changing password', response);
	if (!response.success) {
		toastMessage(response.message, TOAST_MESSAGE.ERROR);
		console.error(response.message);
	} else {
		form.reset();
		toastMessage(response.message, TOAST_MESSAGE.SUCCESS);
		console.log(response.message);
	}
};

checkPassword = function (form) {
	if (form.password.value !== form.password_repeat.value) {
		invalid(form.password_repeat, 'Passwords must match!');
		return false;
	}
	if (form.password.value.length < MIN_LENGTH_PASSWORD) {
		invalid(
			form.password,
			`Password must be at least ${MIN_LENGTH_PASSWORD} characters long!`
		);
		return false;
	}
	return true;
};

reloadMessages = function (token, email) {
	if (!token) {
		token = getToken();
	}
	if (!email) {
		email = document.getElementById('email').innerText;
	}
	clearHistory();

	const res = serverstub.getUserMessagesByEmail(token, email);

	if (!res.success) {
		console.error(res.message);
		toastMessage(res.message, TOAST_MESSAGE.ERROR);
		return;
	}

	const data = res.data;
	// console.log(data);

	const history = document.getElementById('history');
	for (const message of data) {
		const messageContainer = document.createElement('div');
		messageContainer.className = 'message';

		const messageProfile = document.createElement('div');
		messageProfile.className = 'profile_information';
		messageProfile.innerHTML = `<span>${message.writer}</span> posted`;
		messageContainer.appendChild(messageProfile);

		const messageContent = document.createElement('div');
		messageContent.className = 'message_content';
		messageContent.innerText = message.content;
		messageContainer.appendChild(messageContent);

		history.appendChild(messageContainer);
	}
	// toastMessage('User messages updated!', TOAST_MESSAGE.SUCCESS);
};

invalid = function (element, message) {
	element.setCustomValidity(message);
	element.reportValidity();
};

postMessage = function (token, email) {
	if (!token) {
		token = getToken();
	}
	if (!email) {
		email = document.getElementById('email').innerText;
	}
	const content = document.post.message.value;
	if (!content || content.trim() === '') {
		return;
	}
	// console.log(token, content, email);
	const res = serverstub.postMessage(token, content, email);
	if (!res.success) {
		console.error(res.message);
		toastMessage(res.message, TOAST_MESSAGE.ERROR);
		return;
	}

	document.post.message.value = '';
	reloadMessages(token);
	toastMessage(res.message, TOAST_MESSAGE.SUCCESS);
};

/*****
	NAVIGATION
*****/
changeTab = function (tab) {
	for (t of PROFILE_TABS) {
		document.getElementById(t).dataset.show = 'false';
	}
	const tabItems = document.querySelectorAll('.navbar > ul > li');
	for (item of tabItems) {
		if (item.dataset.active === '') {
			delete item.dataset.active;
		}
	}

	document.querySelector(`.navbar > ul > li.${tab}`).dataset.active = '';
	document.getElementById(tab).dataset.show = 'true';
};

/*****
	UPDATE DATA
*****/
updateProfileInformation = function (token, email) {
	// console.log(token, email);
	let response;
	const activeUser = serverstub.getUserDataByToken(token);
	if (email) {
		response = serverstub.getUserDataByEmail(token, email);
	} else {
		response = activeUser;
	}
	const data = response.data;

	if (!response.success || !data) {
		console.error(response.message);
		toastMessage(response.message, TOAST_MESSAGE.ERROR);
		return;
	}

	const retButton = document.querySelector(
		'#home > .personal_information > .return'
	);
	if (data.email !== activeUser.data.email) {
		retButton.classList.remove('hidden');
	} else {
		retButton.classList.add('hidden');
	}

	document.getElementById(
		'fullname'
	).innerText = `${data.firstname} ${data.familyname}`;
	document.getElementById('gender').innerText = data.gender;
	document.getElementById('email').innerText = data.email;
	document.getElementById(
		'location'
	).innerText = `${data.city}, ${data.country}`;

	reloadMessages(token);
};

clearSearchResults = function () {
	document.getElementById('search_results').innerHTML = '';
};

clearHistory = function () {
	document.getElementById('history').innerHTML = '';
};

/****
	SEARCH USER
****/
searchUser = function (token) {
	const search = document.search.searchbar.value;
	const response = serverstub.getUserDataByEmail(token, search);
	if (!response.success) {
		console.error(response.message);
		document.getElementById('search_results').innerText = response.message;
		toastMessage(response.message, TOAST_MESSAGE.ERROR);
		return;
	}
	const data = response.data;
	if (!data) {
		console.error('No data returned!');
		document.getElementById('search_result').innerText =
			'Search failed, please try again!';
		toastMessage('No data returned!', TOAST_MESSAGE.ERROR);
		return;
	}

	const container = document.createElement('div');
	container.className = 'user';
	container.innerHTML = `${data.firstname} ${data.familyname}, ${data.email}`;
	container.addEventListener('click', () => {
		// console.log('click', data);
		updateProfileInformation(getToken(), data.email);
		changeTab('home');
	});

	document.getElementById('search_results').innerHTML = '';
	document.getElementById('search_results').appendChild(container);
};

/*****
	TOAST MESSAGES
*****/
const TOAST_MESSAGE = {SUCCESS: 'success', ERROR: 'error', INFO: 'info'};

toastMessage = function (message, type) {
	// console.log(typeof type);
	if (typeof type === 'string') {
		toast.classList.add(type.toLowerCase());
	} else {
		type = '';
	}
	toast.innerText = message;
	toast.classList.add('show');

	setTimeout(() => {
		toast.classList.remove('show');
		toast.classList.remove(type.toLowerCase());
	}, 1500);
};
