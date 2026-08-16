export class AdminRegistrationFormData {
    constructor(username, password, firstName, lastName, email, phone) {
        this.username = username;
        this.password = password;
        this.firstName = firstName;
        this.lastName = lastName;
        this.email = email;
        this.phone = phone;
    }

    static fromRegistrationData(data) {
        return new AdminRegistrationFormData(
            data.username.value,
            data.password.value,
            data.firstName.value,
            data.lastName.value,
            data.email.value,
            data.phone.value || null
        );
    }

    toJSON() {
        return {
            username: this.username,
            password: this.password,
            first_name: this.firstName,
            last_name: this.lastName,
            mail: this.email,
            phone: this.phone
        };
    }
}
