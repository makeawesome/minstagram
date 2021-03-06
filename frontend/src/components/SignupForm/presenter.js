import React from "react"
import PropTypes from "prop-types"
import FacebookLogin from "react-facebook-login"
import formStyles from "components/shared/formStyles.scss"

const SignupForm = (props, context) => (
  <div className={formStyles.formComponent}>
      <h3 className={formStyles.signupHeader}>Sign up to see photos and videos from your friends.</h3>
      <FacebookLogin
        appId="204672523417751"
        autoLoad={false}
        fields="name, email, picture"
        callback={props.handleFacebookLogin}
        cssClass={formStyles.button}
        icon="fa-facebook-official"
        textButton={context.t("Log in with Facebook")}
      />
      <span className={formStyles.divider}>or</span>
      <form className={formStyles.form} onSubmit={props.handleSubmit}>
          <input 
            type="email" 
            placeholder="Email"
            className={formStyles.textInput}
            value={props.emailValue}
            onChange={props.handleInputChange}
            name="email"
          />
          <input
            type="text"
            placeholder="Full Name"
            className={formStyles.textInput}
            value={props.fullnameValue}
            onChange={props.handleInputChange}
            name="fullname"
          />
          <input
            type="username"
            placeholder="Username"
            className={formStyles.textInput}
            value={props.usernameValue}
            onChange={props.handleInputChange}
            name="username"
          />
          <input
            type="password"
            placeholder="Password"
            className={formStyles.textInput}
            value={props.passwordValue}
            onChange={props.handleInputChange}
            name="password"
          />
          <input
            type="submit"
            placeholder="Sign up"
            className={formStyles.button}
          />
      </form>
      <p className={formStyles.terms}>
          By signing up, you agree to our <span>Terms & Privacy Policy</span>
      </p>
  </div>
);

SignupForm.propTypes = {
  emailValue: PropTypes.string.isRequired,
  fullnameValue: PropTypes.string.isRequired,
  usernameValue: PropTypes.string.isRequired,
  passwordValue: PropTypes.string.isRequired,
  handleInputChange: PropTypes.func.isRequired,
  handleSubmit: PropTypes.func.isRequired,
  handleFacebookLogin: PropTypes.func.isRequired
}

SignupForm.contextTypes = {
  t: PropTypes.func.isRequired
}

export default SignupForm;