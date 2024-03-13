let initialized;

let currentState;
const urls = {
	login: '/profile/home', // user is logged in
	logout: '/login', // user is logged out
};

window.addEventListener('popstate', (event) => {
	if (event.state.signinState !== currentState) {
		history.replaceState(
			{currentState, resetProfile: false},
			'',
			urls[currentState]
		);
	}

	if (currentState === 'login') {
		const token = getToken();

		let signedIn;
		server
			.checkToken(token)
			.then(() => {
				// logged in
				signedIn = true;
			})
			.catch(() => {
				// logged out
				signedIn = false;
			})
			.finally(() => {
				// changed state
				if (signedIn) {
					changeTab(
						document.location.pathname.replace('/profile/', ''),
						event.state.profile,
						false
					);
				}
			});
	} else {
		if (document.location.pathname === '/login') {
			loadLoginPage(undefined, false);
		} else {
			loadSignupPage(false);
		}
	}
});

const Router = {
	push: (route, profile) => {
		const signinState = route.includes('profile') ? 'login' : 'logout';

		if (!initialized) {
			currentState = signinState;
			initialized = true;

			history.replaceState(
				{
					signinState,
					profile,
				},
				'',
				route
			);
		} else {
			history.pushState(
				{
					signinState,
					profile,
				},
				'',
				route
			);
		}
	},
};

const changeState = (state) => {
	currentState = state;
};
