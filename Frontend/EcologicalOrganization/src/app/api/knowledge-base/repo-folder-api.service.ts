import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { map, Observable } from 'rxjs';
import { WRITING_ASSISTANT_API_URL } from '../common/api-url';
import { Page, PageDto, toPage } from '../common/page.model';
import { RepoFolder, RepoFolderDto, toRepoFolder } from './knowledge-base.model';

@Injectable({ providedIn: 'root' })
export class RepoFolderApiService {
  private readonly url = `${WRITING_ASSISTANT_API_URL}/repo-folders`;

  constructor(private http: HttpClient) {}

  list(parentId: number | null = null, page = 1, perPage = 100): Observable<Page<RepoFolder>> {
    const params: Record<string, number> = { page, per_page: perPage };
    if (parentId !== null) params['parent_id'] = parentId;
    return this.http
      .get<PageDto<RepoFolderDto>>(this.url, { params })
      .pipe(map((dto) => toPage(dto, toRepoFolder)));
  }

  get(id: number): Observable<RepoFolder> {
    return this.http.get<RepoFolderDto>(`${this.url}/${id}`).pipe(map(toRepoFolder));
  }

  create(name: string, parentId: number | null = null): Observable<RepoFolder> {
    const body: { name: string; parent_id?: number } = { name };
    if (parentId !== null) body.parent_id = parentId;
    return this.http.post<RepoFolderDto>(this.url, body).pipe(map(toRepoFolder));
  }

  rename(id: number, name: string): Observable<RepoFolder> {
    return this.http.patch<RepoFolderDto>(`${this.url}/${id}`, { name }).pipe(map(toRepoFolder));
  }

  delete(id: number): Observable<void> {
    return this.http.delete<void>(`${this.url}/${id}`);
  }
}
