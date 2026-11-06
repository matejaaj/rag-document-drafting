export type RoleType = 'EMPLOYEE' | 'MANAGER';

export interface Registration {
  name: string;
  surname: string;
  email: string;
  password: string;

  roles: {
    subsystem: 'WA';
    role: RoleType;
  }[];
}
