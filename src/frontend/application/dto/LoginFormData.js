export class LoginFormData {
    constructor(username, password) {
        this.username = username;
        this.password = password;
    }

    static fromCredentials(credentials) {
        return new LoginFormData(
            credentials.username.value,
            credentials.password.value
        );
    }

    toJSON() {
        return {
            username: this.username,
            password: this.password
        };
    }
}
