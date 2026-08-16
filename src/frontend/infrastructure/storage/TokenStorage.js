export class TokenStorage {
    constructor() {
        this.tokenKey = 'access_token';
        this.tokenTypeKey = 'token_type';
    }

    save(token, tokenType = 'bearer') {
        localStorage.setItem(this.tokenKey, token);
        localStorage.setItem(this.tokenTypeKey, tokenType);
    }

    getToken() {
        return localStorage.getItem(this.tokenKey);
    }

    getTokenType() {
        return localStorage.getItem(this.tokenTypeKey) || 'bearer';
    }

    getAuthorizationHeader() {
        const token = this.getToken();
        if (!token) return null;
        return `${this.getTokenType()} ${token}`;
    }

    clear() {
        localStorage.removeItem(this.tokenKey);
        localStorage.removeItem(this.tokenTypeKey);
    }

    isAuthenticated() {
        return !!this.getToken();
    }
}
