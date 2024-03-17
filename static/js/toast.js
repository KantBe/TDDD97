let toastElement;

const TOAST_MESSAGE = {SUCCESS: 'success', ERROR: 'error', INFO: 'info'};
let timeoutId;

const toast = {
	error: (message) => {
		toastMessage(message, TOAST_MESSAGE.ERROR);
	},
	success: (message) => {
		toastMessage(message, TOAST_MESSAGE.SUCCESS);
	},
	info: (message) => {
		toastMessage(message, TOAST_MESSAGE.INFO);
	},
	login: () => {
		if (!toastElement) {
			init();
		}
		toastElement.classList.add('logged-in');
	},
	logout: () => {
		if (!toastElement) {
			init();
		}
		toastElement.classList.remove('logged-in');
	},
};

const init = () => {
	toastElement = document.createElement('div');
	toastElement.classList = [];
	toastElement.id = 'toast';
	document.body.appendChild(toastElement);
};

toastMessage = function (message, type) {
	if (!toastElement) {
		init();
	}
	// we either log or error the toast as well
	(console[type] || console.log)(message);
	// super simple toast messager
	if (typeof type === 'string') {
		toastElement.classList.add(type.toLowerCase());
	} else {
		type = '';
	}
	toastElement.innerText = message;
	toastElement.classList.add('show');

	if (timeoutId) {
		clearInterval(timeoutId);
	}
	timeoutId = setTimeout(() => {
		toastElement.classList.remove('show');
		toastElement.classList.remove(type.toLowerCase());
		timeoutId = undefined;
	}, 2300);
};
