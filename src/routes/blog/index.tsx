// @ts-nocheck
import { createSignal, createMemo, Show } from 'solid-js';
import { useNavigate } from '@solidjs/router';
import { SiteLayout } from '../../components/layouts/SiteLayout';
import { ListView } from '../../components/organisms/ListView';
import { useTheme } from '../../stores/theme';
import { useI18n } from '../../stores/i18n';
import { usePortfolio } from '../../stores/content';
import { Skeleton } from '../../components/atoms/Skeleton';

export default function BlogPage() {
  const { isDark, toggleTheme } = useTheme();
  const { lang, toggleLang, ui } = useI18n();
  const { data } = usePortfolio();
  const navigate = useNavigate();

  const [selectedTag, setSelectedTag] = createSignal(null);
  const [searchText, setSearchText] = createSignal('');

  const filteredPosts = createMemo(() => {
    if (!data()) return [];
    return data().posts.filter((post) => {
      const matchesTag = selectedTag() ? post.tags.includes(selectedTag()) : true;
      const matchesSearch = searchText()
        ? post.title.toLowerCase().includes(searchText().toLowerCase()) || post.desc.toLowerCase().includes(searchText().toLowerCase())
        : true;
      return matchesTag && matchesSearch;
    });
  });

  const clearFilters = () => {
    setSelectedTag(null);
    setSearchText('');
  };

  return (
    <SiteLayout ui={ui()} lang={lang()} toggleLang={toggleLang} isDark={isDark()} toggleTheme={toggleTheme} data={data()}>
      <Show
        when={!data.loading}
        fallback={
          <div class="space-y-4 py-12">
            <Skeleton class="h-8 w-48" />
            <Skeleton class="h-10 w-full rounded-xl" />
            <Skeleton class="h-32 w-full rounded-xl" />
            <Skeleton class="h-32 w-full rounded-xl" />
          </div>
        }
      >
        <ListView 
          type="blog"
          ui={ui()}
          filteredPosts={filteredPosts()}
          filteredProjects={[]}
          searchText={searchText()}
          setSearchText={setSearchText}
          selectedTag={selectedTag()}
          clearFilters={clearFilters}
          onItemClick={(item) => navigate(`/blog/${item.slug}`)}
          onTagClick={(tag) => setSelectedTag(tag)}
        />
      </Show>
    </SiteLayout>
  );
}
