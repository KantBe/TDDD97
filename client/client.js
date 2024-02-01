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
	// first we reset our content div
	document.getElementById('content').innerHTML = '';

	// then we get our current saved token and user
	const token = getToken();
	const users = JSON.parse(localStorage.getItem('loggedinusers'));

	if (token && users && users[token]) {
		// user is logged in
		// update view and message display
		displayView('profileView');
		toast.classList.add('logged-in');

		// we clear all our test data
		clearHistory();
		clearSearchResults();
		// and insert our current data
		updateProfileInformation(token);

		// then we switch to the correct tab
		const tab = sessionStorage.getItem('activeTab');
		if (!tab || !PROFILE_TABS.includes(tab)) {
			sessionStorage.setItem('activeTab', 'home');
		}
		changeTab(sessionStorage.getItem('activeTab'));

		// and add some event listeners for the forms
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
		// user is not logged in
		if (token) {
			// we remove the token
			localStorage.removeItem('token');
		}
		if (users) {
			// and the logged in users
			localStorage.setItem('loggedinusers', '{}');
		}

		// we display our sign up view
		displayView('welcomeView');

		// and add the event listeners for our forms
		document.signup.addEventListener('submit', (e) => {
			e.preventDefault();
			signup();
		});
		document.login.addEventListener('submit', function (e) {
			e.preventDefault();
			login(document.login.email.value, document.login.password.value);
		});
	}
};

window.onload = function () {
	// this is for message display, needs to be done once per page load
	toast = document.getElementById('toast');
	toast.classList = [];

	// on window load, we refresh the page to update our content div
	refresh();
};

signup = function () {
	const form = document.signup;
	// first, we check if the password meets the criteria
	if (!checkPassword(form)) {
		return;
	}

	// then we put our data into a JS-object
	const data = {
		email: form.email.value,
		password: form.password.value,
		firstname: form.firstname.value,
		familyname: form.lastname.value,
		gender: form.gender.value,
		city: form.city.value,
		country: form.country.value,
	};

	// and sign up the user
	const res = serverstub.signUp(data);
	if (res.success) {
		// on success, we print a success message and sign in the user
		toastMessage(res.message, TOAST_MESSAGE.SUCCESS);
		login(data.email, data.password);
	} else {
		// on error, we print the error message to the user
		toastMessage(res.message, TOAST_MESSAGE.ERROR);
		console.error('error signing up user', res.message);
	}
};

login = function (email, password) {
	// try to sign in the user
	const res = serverstub.signIn(email, password);

	if (res.success) {
		// in case of success, we reset our tab to home, set the token and refresh the page
		sessionStorage.setItem('activeTab', 'home');
		localStorage.setItem('token', res.data);
		refresh();

		// also print out success message at the end
		toastMessage(res.message, TOAST_MESSAGE.SUCCESS);
	} else {
		// print error message if the login was not successful
		toastMessage(res.message, TOAST_MESSAGE.ERROR);
	}
};

logout = function () {
	// user wants to log out
	// so we get the token  and log out the user from the item
	const token = getToken();
	const res = serverstub.signOut(token);
	if (res.success) {
		// this should always succeed if the user didn't mess around with the local storage
		localStorage.removeItem('token');
	}

	// we refresh our page
	refresh();

	// and send a confirmation message to the user
	toast.classList.remove('logged-in');
	toastMessage(res.message, TOAST_MESSAGE.SUCCESS);
};

changePassword = function () {
	// check the password requirements first
	const form = document.password_reset;
	if (!checkPassword(form)) {
		return;
	}

	// then change the password
	const response = serverstub.changePassword(
		getToken(),
		form.password_old.value,
		form.password.value
	);

	if (response.success) {
		// on success, show success message and empty the form
		form.reset();
		toastMessage(response.message, TOAST_MESSAGE.SUCCESS);
		console.log(response.message);
	} else {
		// on error display error message
		toastMessage(response.message, TOAST_MESSAGE.ERROR);
		console.error(response.message);
	}
};

checkPassword = function (form) {
	// check the password for matching values and min length
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

reloadMessages = function (token) {
	// reload all the messages from the user with the given token and email
	if (!token) {
		token = getToken();
	}
	email = document.getElementById('email').innerText;

	// delete all messages
	clearHistory();

	// get all messages by user and mail
	const res = serverstub.getUserMessagesByEmail(token, email);

	// if there is an error, show it to the user
	if (!res.success) {
		console.error(res.message);
		toastMessage(res.message, TOAST_MESSAGE.ERROR);
		return;
	}

	// now get all the data
	const data = res.data;
	console.log(data);

	// and add it to the message history
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
	// inform user in case it's needed
	toastMessage('User messages updated!', TOAST_MESSAGE.SUCCESS);
};

invalid = function (element, message) {
	// mark a field as invalid
	element.setCustomValidity(message);
	element.reportValidity();
};

postMessage = function (token, email) {
	// we check if token and mail are given
	if (!token) {
		token = getToken();
	}
	if (!email) {
		email = document.getElementById('email').innerText;
	}

	// then we retrieve the content
	const content = document.post.message.value;
	// and check if it's empty
	if (!content || content.trim() === '') {
		return;
	}
	// console.log(token, content, email);
	// then we post the message
	const res = serverstub.postMessage(token, content, email);
	if (!res.success) {
		// on error, we display an error message
		console.error(res.message);
		toastMessage(res.message, TOAST_MESSAGE.ERROR);
		return;
	}

	// on success, we update all values and reload the messages
	document.post.reset();
	reloadMessages(token);
	toastMessage(res.message, TOAST_MESSAGE.SUCCESS);
};

/*****
	NAVIGATION
*****/
changeTab = function (tab, resetProfile) {
	// in case changeTab was called from clicking the tabs, resetProfile is not set, so we set it to true
	if (resetProfile === undefined || resetProfile === null) {
		resetProfile = true;
	}

	// we reset all the divs
	for (t of PROFILE_TABS) {
		document.getElementById(t).dataset.show = 'false';
	}
	// and reset all the navbar items
	const tabItems = document.querySelectorAll('.navbar > ul > li');
	for (item of tabItems) {
		if (item.dataset.active === '') {
			delete item.dataset.active;
		}
	}

	// then we reset the profile if needed
	if (resetProfile && tab === 'home') {
		updateProfileInformation(getToken());
	}

	// update the session storage (to stay on the correct tab even after browser refresh)
	sessionStorage.setItem('activeTab', tab);

	// and update our div and navbar item
	document.querySelector(`.navbar > ul > li.${tab}`).dataset.active = '';
	document.getElementById(tab).dataset.show = 'true';
};

/*****
	UPDATE DATA
*****/
updateProfileInformation = function (token, email) {
	// console.log(token, email);
	// this is the profile on the home page
	let response;
	// first we get the active user
	const activeUser = serverstub.getUserDataByToken(token);
	if (email) {
		// if email is set, we want to load a different user
		response = serverstub.getUserDataByEmail(token, email);
	} else {
		response = activeUser;
	}
	// then we load the data
	const data = response.data;

	if (!response.success || !data) {
		// if there was an error retrieving the messages, we display it to the user
		console.error(response.message);
		toastMessage(response.message, TOAST_MESSAGE.ERROR);
		return;
	}

	// we then display or hide the return button (for getting back to the own profile)
	const retButton = document.querySelector(
		'#home > .personal_information > .return'
	);
	// based on the matching email
	if (data.email !== activeUser.data.email) {
		retButton.classList.remove('hidden');
	} else {
		retButton.classList.add('hidden');
	}

	// then we set all the profile information
	document.getElementById(
		'fullname'
	).innerText = `${data.firstname} ${data.familyname}`;
	document.getElementById('gender').innerText = data.gender;
	document.getElementById('email').innerText = data.email;
	document.getElementById(
		'location'
	).innerText = `${data.city}, ${data.country}`;

	// and update the messages
	reloadMessages(token);
};

clearSearchResults = function () {
	// this just empties the search results
	document.getElementById('search_results').innerHTML = '';
};

clearHistory = function () {
	// this just empties the messages
	document.getElementById('history').innerHTML = '';
};

/****
	SEARCH USER
****/
searchUser = function (token) {
	// in case we want to search for a user
	// we first get the searched value
	const search = document.search.searchbar.value;

	// then we search if a user with that email exists
	const response = serverstub.getUserDataByEmail(token, search);
	if (!response.success) {
		// if not, we show an error
		console.error(response.message);
		document.getElementById('search_results').innerText = response.message;
		toastMessage(response.message, TOAST_MESSAGE.ERROR);
		return;
	}
	// if data was returned, we check it
	const data = response.data;
	if (!data) {
		// no data means the search somehow still failed, so we still display an error
		console.error('No data returned!');
		document.getElementById('search_result').innerText =
			'Search failed, please try again!';
		toastMessage('No data returned!', TOAST_MESSAGE.ERROR);
		return;
	}

	// we update the search field to show the new user
	const container = document.createElement('div');
	container.className = 'user';
	container.innerHTML = `${data.firstname} ${data.familyname}, ${data.email}`;
	container.addEventListener('click', () => {
		// console.log('click', data);
		updateProfileInformation(getToken(), data.email);
		changeTab('home', false);
	});
	document.getElementById('search_results').innerHTML = '';
	document.getElementById('search_results').appendChild(container);
};

/*****
	TOAST MESSAGES
*****/
const TOAST_MESSAGE = {SUCCESS: 'success', ERROR: 'error', INFO: 'info'};
let timeoutId;

toastMessage = function (message, type) {
	// super simple toast messager
	// console.log(typeof type);
	if (typeof type === 'string') {
		toast.classList.add(type.toLowerCase());
	} else {
		type = '';
	}
	toast.innerText = message;
	toast.classList.add('show');

	if (timeoutId) {
		clearInterval(timeoutId);
	}
	timeoutId = setTimeout(() => {
		toast.classList.remove('show');
		toast.classList.remove(type.toLowerCase());
		timeoutId = undefined;
	}, 1500);
};
