
export class ServiceException extends Error {

  constructor(type, reason) {
    const message = "type = " + type + "; reason=" + reason;
    super(message);
    this.type = type;
    this.reason = reason;
  }
}

export const TYPE_DEFAULT_ERROR = 'default_error ';
