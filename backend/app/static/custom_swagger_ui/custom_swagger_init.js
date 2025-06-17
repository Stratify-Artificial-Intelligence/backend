// Utility function to wait for an element
const waitForElement = (selector) => {
  return new Promise(resolve => {
    if (document.querySelector(selector)) {
      return resolve(document.querySelector(selector));
    }

    const observer = new MutationObserver(() => {
      if (document.querySelector(selector)) {
        observer.disconnect();
        resolve(document.querySelector(selector));
      }
    });

    observer.observe(document.body, {
      childList: true,
      subtree: true
    });
  });
};

window.onload = async function() {
  // Firebase init
  // FIREBASE_CONFIG is injected in app/app/main.py
  const firebaseConfig = JSON.parse(FIREBASE_CONFIG);
  firebase.initializeApp(firebaseConfig);
  const auth = firebase.auth();

  const loginHtml = await fetch(`/static/custom_swagger_ui/google_login_button.html`)
    .then(res => res.text());

  const authorizeWrapper = await waitForElement('.auth-wrapper');

  const loginWrapper = document.createElement('div');
  loginWrapper.innerHTML = loginHtml;
  loginWrapper.id = 'google-login-wrapper';
  loginWrapper.style.display = 'inline-block';
  loginWrapper.style.marginLeft = '10px';

  if (authorizeWrapper) {
    authorizeWrapper.appendChild(loginWrapper);
  }

  async function handleAuthentication(user) {
    if (user) {
      try {
        const token = await user.getIdToken();

        // Click the authorize button
        const authButton = await waitForElement('.auth-wrapper .btn.authorize');
        authButton.click();

        // Wait for auth modal to appear
        await waitForElement('.auth-container');

        // Click the logout button (if it exists)
        const logoutButton = await waitForElement('.auth-container button');
        logoutButton.click();

        // Fill input with token
        // Note: Using the nativeInputValueSetter is a workaround to set the value of the
        // input field because Swagger UI does not trigger the input event when setting
        // the value directly.
        const tokenInput = await waitForElement('.auth-container input[type="text"]');
        const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
        nativeInputValueSetter.call(tokenInput, `${token}`);
        tokenInput.dispatchEvent(new Event('input', { bubbles: true }));

        // Submit the form
        // const submitButton = await waitForElement('.auth-container .authorize');
        // submitButton.click();
      } catch (error) {
        console.error('Failed to authorize Swagger UI:', error);
      }
    }
  }

  const loginButton = await waitForElement('#google-login-button');
  loginButton.addEventListener('click', () => {
    const provider = new firebase.auth.GoogleAuthProvider();

    // Option 1: Sign in with pop-up
    auth.signInWithPopup(provider).then(async (result) => {
      await handleAuthentication(result.user)
    });

    // Option 2: Sign in with redirect
    // auth.signInWithRedirect(provider);
  });

  // Option 2: Sign in with redirect
  // auth.onAuthStateChanged(async function(user) {
  //   await handleAuthentication(user);
  // })
};
