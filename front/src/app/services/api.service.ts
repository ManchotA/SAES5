import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { Partie, SallePublique } from './models';

@Injectable({ providedIn: 'root' })
export class ApiService {
  private http = inject(HttpClient);

  getSalles(): Promise<SallePublique[]> {
  return firstValueFrom(this.http.get<SallePublique[]>('/api/salles'))
    .then(s => [...s].sort((a, b) => a.etage - b.etage));
}

  getPartie()      { return firstValueFrom(this.http.get<Partie>('/api/partie')); }
  nouvellePartie() { return firstValueFrom(this.http.post<Partie>('/api/partie', {})); }

  lancerEnigme(id: string) {
    return firstValueFrom(this.http.post(`/api/partie/salles/${id}/enigme`, {}));
  }
  annulerEnigme(id: string) {
    return firstValueFrom(this.http.delete(`/api/partie/salles/${id}/enigme`));
  }
}