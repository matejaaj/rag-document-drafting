export interface PageMeta {
  page: number;
  perPage: number;
  totalCount: number;
}

export interface Page<T> {
  items: T[];
  meta: PageMeta;
}

export interface PageMetaDto {
  page: number;
  per_page: number;
  total_count: number;
}

export interface PageDto<T> {
  items: T[];
  meta: PageMetaDto;
}

export function toPageMeta(dto: PageMetaDto): PageMeta {
  return { page: dto.page, perPage: dto.per_page, totalCount: dto.total_count };
}

export function toPage<TDto, T>(dto: PageDto<TDto>, toItem: (item: TDto) => T): Page<T> {
  return { items: (dto.items || []).map(toItem), meta: toPageMeta(dto.meta) };
}
