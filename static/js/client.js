const MIN_LENGTH_PASSWORD = 8;
const PROFILE_TABS = ['home', 'browse', 'account'];

var position = {latitude:0, longitude:0};

getToken = function () {
	return localStorage.getItem('token');
};

window.onload = function () {
	// on window load, we refresh the page to update our content div
	refresh();
};

displayView = function (id) {
	// the code required to display a view
	const view = document.getElementById(id);
	document.getElementById('content').innerHTML = view.innerHTML;
};

refresh = function (signupPage) {
	console.log('refreshing', signupPage);
	// first we reset our content div
	document.getElementById('content').innerHTML = '';

	// then we get our current saved token and user
	const token = getToken();
	if (!token) {
		// we remove the token
		localStorage.removeItem('token');
		// and load the login page

		if (signupPage) {
			loadSignupPage();
		} else {
			loadLoginPage(signupPage);
		}
		return;
	}

	// we only check the token if it is set
	server
		.checkToken(token)
		.then(() => {
			// user is logged in
			server.websocket(token);
			loadProfile(token);
		})
		.catch(() => {
			// we remove the token
			localStorage.removeItem('token');
			if (signupPage) {
				loadSignupPage();
			} else {
				loadLoginPage(signupPage);
			}
		});
};

loadProfile = function (token) {
	// update view and message display
	displayView('profileView');
	toastElement.classList.add('logged-in');

	// we clear all our test data
	clearHistory();
	clearSearchResults();

	// then we switch to the correct tab
	const tab = sessionStorage.getItem('activeTab');
	if (!tab || !PROFILE_TABS.includes(tab)) {
		sessionStorage.setItem('activeTab', 'home');
	}
	// changeTab also inserts new data
	changeTab(sessionStorage.getItem('activeTab'), null);

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
};

loadLoginPage = (signupPage, push) => {
	if (signupPage === undefined && document.location.pathname === '/signup') {
		loadSignupPage();
		return;
	}
	if (push !== false) {
		Router.push('/login');
	}
	// display login view
	displayView('loginView');

	document.login.addEventListener('submit', (e) => {
		e.preventDefault();
		login(document.login.email.value, document.login.password.value);
	});
};

loadSignupPage = (push) => {
	if (push !== false) {
		Router.push('/signup');
	}
	// display sign up view
	displayView('signupView');
	// and add the event listeners for our forms
	document.signup.addEventListener('submit', (e) => {
		e.preventDefault();
		signup();
	});
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
	server
		.signUp(data)
		.then((res) => {
			// on success, we print a success message and sign in the user
			toast.success('User signed up successfully');
			login(data.email, data.password);
		})
		.catch((error) => {
			// on error, we print the error message to the user
			if (error.status === 409) {
				invalid(form.email, '');
				toast.error(
					'User with this email already exists, please choose another email or login!'
				);
			} else if (
				error.status === 400 ||
				error.status === 405 ||
				error.status === 500
			) {
				toast.error(
					'There was an error with the system, please reload the page and try again!'
				);
			}
		});
};

login = function (email, password) {
	changeState('login');
	// try to sign in the user
	server
		.signIn(email, password)
		.then((res) => {
			// in case of success, we reset our tab to home, set the token and refresh the page
			sessionStorage.setItem('activeTab', 'home');
			localStorage.setItem('token', res.response.data);
			refresh();

			// also print out success message at the end
			toast.success('Successfully logged in');
		})
		.catch((err) => {
			// print error message if the login was not successful
			if (err.status === 401) {
				toast.error('Wrong username or password');
			} else if (err.status === 400 || err.status === 405) {
				toast.error(err.response.message);
			} else if (err.status === 500) {
				toast.error(
					'There was an error processing your request, please try again!'
				);
			}
		});
};

logout = function () {
	changeState('logout');
	// user wants to log out
	// so we get the token  and log out the user from the item
	const token = getToken();
	server.signOut(token).finally(() => {
		localStorage.removeItem('token');

		// we refresh our page
		refresh();

		// and send a confirmation message to the user
		toastElement.classList.remove('logged-in');
		toast.success('User logged out successfully');
	});
};

changePassword = function () {
	// check the password requirements first
	const form = document.password_reset;
	if (!checkPassword(form)) {
		return;
	}

	// then change the password
	server
		.changePassword(getToken(), form.password_old.value, form.password.value)
		.then((res) => {
			// on success, show success message and empty the form
			form.reset();
			toast.success('Password changed successfully');
		})
		.catch((error) => {
			if (error.status === 401) {
				invalid(form.password_old, 'Wrong password!');
				toast.error('Wrong password!');
			} else if (error.status === 400) {
				// on error display error message
				toast.error(error.response.message);
			}
		});
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
	server
		.getUserMessagesByEmail(token, email)
		.then((res) => {
			displayMessageHistory(res.response.data, email);
			// inform user in case it's needed
			toast.success('User messages updated!');
		})
		.catch(() => {
			toast.error(
				'There was an error updating the messages, please reload the page!'
			);
		});
};

displayMessageHistory = async (data, email) => {
	// and add it to the message history
	const history = document.getElementById('history');
	for (const message of data) {
		const messageContainer = document.createElement('div');
		messageContainer.className = `message ${
			email === message.writer ? 'own' : 'other'
		}`;

		geodata = await convertGeocode(message.latitude, message.longitude);

		const messageProfile = document.createElement('div');
		messageProfile.className = 'profile_information';
		messageProfile.innerHTML = `<span>${message.writer}</span> posted from <span>${geodata.city}</span>`;
		messageContainer.appendChild(messageProfile);

		const messageContent = document.createElement('div');
		messageContent.className = 'message_content';
		messageContent.innerText = message.message;
		messageContainer.appendChild(messageContent);

		history.appendChild(messageContainer);
	}
};

convertGeocode = function (latitude, longitude) {
	return fetchAsync('https://geocode.xyz/'+latitude+','+longitude+'?json=1');
}

fetchAsync = async function (url) {
  let response = await fetch(url);
  return response.json();
}

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
	// then we get the position
	if (navigator.geolocation) {
		navigator.geolocation.getCurrentPosition(getPosition);
  	} else {
    	console.log('location', "Geolocation is not supported by this browser.");
  	}
	// then we post the message
	server
		.postMessage(token, content, email, position)
		.then((res) => {
			// on success, we update all values and reload the messages
			document.post.reset();
			reloadMessages(token);
			toast.success('Message posted!');
		})
		.catch((error) => {
			// on error, we display an error message
			toast.error(
				'There was an error posting the message, please reload the page and try again!'
			);
			return;
		});
};

getPosition = function(currentPosition) {
	position.latitude = currentPosition.coords.latitude;
	position.longitude = currentPosition.coords.longitude;
}

/*****
	NAVIGATION
*****/
changeTab = function (tab, profile, pushRoute) {
	if (pushRoute !== false) {
		Router.push('/profile/' + tab, profile);
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
	if (tab === 'home') {
		updateProfileInformation(getToken(), profile);
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
updateProfileInformation = async function (token, email) {
	// this is the profile on the home page
	let response;
	// first we get the active user
	const activeUser = (await server.getUserDataByToken(token)).response;
	if (email) {
		// if email is set, we want to load a different user
		try {
			response = (await server.getUserDataByEmail(token, email)).response;
		} catch (error) {
			console.error(error);
			toast.error(`There was an error displaying user ${email}`);
			response = activeUser;
		}
	} else {
		response = activeUser;
	}
	// then we load the data
	const data = response.data;

	if (!data) {
		// if there was an error retrieving the messages, we display it to the user
		toast.error(response.message);
		return;
	}

	// we then display or hide the return button (for getting back to the own profile)
	const retButton = document.querySelector(
		'#home > .personal_information > .return'
	);
	// based on the matching email
	if (data[0] !== activeUser.data[0]) {
		retButton.classList.remove('hidden');
	} else {
		retButton.classList.add('hidden');
	}

	// then we set all the profile information
	document.getElementById('fullname').innerText = `${data[1]} ${data[2]}`;
	document.getElementById('gender').innerText = data[3];
	document.getElementById('email').innerText = data[0];
	document.getElementById('location').innerText = `${data[4]}, ${data[5]}`;

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
	server
		.getUserDataByEmail(token, search)
		.then((res) => {
			// if data was returned, we check it
			const data = res.response.data;
			if (!data) {
				// no data means the search somehow still failed, so we still display an error
				document.getElementById('search_result').innerText =
					'Search failed, please try again!';
				toast.error('No data returned!');
			} else {
				updateSearchResults(data);
			}
		})
		.catch((err) => {
			// if not, we show an error
			document.getElementById('search_results').innerText = 'No user found';
			toast.error('No user found');
		});
};

const updateSearchResults = (data) => {
	// we update the search field to show the new user
	const container = document.createElement('div');
	container.className = 'user';
	container.innerHTML = `${data[1]} ${data[2]}, ${data[0]}`;
	container.addEventListener('click', () => {
		// updateProfileInformation(getToken(), data[0]);
		changeTab('home', data[0]);
	});
	document.getElementById('search_results').innerHTML = '';
	document.getElementById('search_results').appendChild(container);
};