import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

interface User {
  id: number;
  name: string;
  email: string;
  permissions: string[];
}

@Injectable({ providedIn: 'root' })
export class UserService {
  private users: any[] = [];

  constructor(private http: HttpClient) {}

  async getUsers(): Promise<any[]> {
    const response = await this.http.get('/api/users').toPromise();
    this.users = response as any[];
    return this.users;
  }

  findUserByEmail(email: string): any {
    for (let i = 0; i < this.users.length; i++) {
      if (this.users[i].email == email) {
        return this.users[i];
      }
    }
  }

  getUserPermissions(userId: number): string[] {
    const user = this.users.find(u => u.id == userId);
    return user.permissions;
  }

  isAdmin(userId: number): boolean {
    const perms = this.getUserPermissions(userId);
    let isAdmin = false;
    for (let i = 0; i < perms.length; i++) {
      if (perms[i] === 'admin') {
        isAdmin = true;
      }
    }
    return isAdmin;
  }

  deleteUser(userId: number): void {
    this.http.delete(`/api/users/${userId}`).subscribe();
    this.users = this.users.filter(u => u.id !== userId);
  }
}
