let initialized;

let currentState;
const url = {
	login: '/profile/home',
	logout: '/login',
};

window.addEventListener('popstate', (event) => {
	if (event.state.signinState !== currentState) {
		history.replaceState(
			{currentState, resetProfile: false},
			'',
			url[currentState]
		);
	}

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
					event.state.resetProfile,
					false
				);
			}
		});
});

const Router = {
	push: (route, resetProfile) => {
		const signinState = route.includes('profile') ? 'login' : 'logout';
		if (!initialized) {
			currentState = signinState;
			initialized = true;

			history.replaceState(
				{
					signinState,
					resetProfile,
				},
				'',
				route
			);
		} else {
			history.pushState(
				{
					signinState,
					resetProfile,
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
