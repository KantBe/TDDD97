const MIN_LENGTH_PASSWORD = 8;

window.onload = () => {
	document.password_reset.addEventListener('submit', (e) => {
		e.preventDefault();
		if (
			!checkPassword(document.password_reset) ||
			document.password_reset.submit.disabled
		) {
			return;
		}
		document.password_reset.submit.disabled = 'disabled';

		const token = document.location.pathname.replace('/reset_password/', '');
		server
			.setPassword(token, document.password_reset.password.value)
			.then((res) => {
				console.log(res);
				toast.success(
					'Password updated successfully, redirecting to main page...'
				);
				setTimeout(() => {
					document.location = '/login';
				}, 2000);
			})
			.catch((err) => {
				console.error(err);
				toast.error(
					'There was an error updating the password, please reload the page and try again!'
				);
			});
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

invalid = function (element, message) {
	// mark a field as invalid
	element.setCustomValidity(message);
	element.reportValidity();
};
