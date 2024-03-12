let initialized;

let prevId;
let id = 0;

let currentState;
let _history = [];

window.addEventListener('popstate', (event) => {
	prevId = id;
	id = event.state.id;
	goingForward = prevId - id < 0;

	if (event.state.signinState !== currentState) {
		console.log(id);
		let delta = 0;
		for (
			let i = id;
			i >= -1 && i <= _history.length;
			i += goingForward ? 1 : -1
		) {
			if (i === -1 || i === _history.length) {
				// there is no state after that
				// return to where you came from
				history.go(goingForward ? -1 : 1);
				return;
			}
			if (_history[i] === currentState) {
				break;
			}
			delta++;
		}
		history.go(delta * goingForward ? 1 : -1);
		return;
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

			_history.push(signinState);

			history.replaceState(
				{
					id: id,
					signinState,
					resetProfile,
				},
				'',
				route
			);
		} else {
			prevId = id;
			history.pushState(
				{
					id: ++id,
					signinState,
					resetProfile,
				},
				'',
				route
			);
			_history.splice(id);
			_history.push(signinState);
		}
		console.log(route, id);
	},
};

const changeState = (state) => {
	currentState = state;
};
