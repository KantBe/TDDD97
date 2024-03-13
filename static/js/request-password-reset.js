window.onload = () => {
	document.request_password_reset.addEventListener('submit', (e) => {
		e.preventDefault();
		if (document.request_password_reset.submit.disabled === 'disabled') {
			return;
		}
		document.request_password_reset.submit.disabled = 'disabled';

		server
			.requestPasswordReset(document.request_password_reset.email.value)
			.then((res) => {
				console.log(res);
				toast.success(
					'Password reset requested successfully, redirecting to main page...'
				);
				setTimeout(() => {
					document.location = '/login';
				}, 2000);
			})
			.catch(() => {
				toast.error(
					'There was an error requesting the password reset, please retry again!'
				);
				document.request_password_reset.submit.disabled = '';
			})
			.finally(() => {
				document.request_password_reset.reset();
			});
	});
};
