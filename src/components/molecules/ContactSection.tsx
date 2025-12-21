// @ts-nocheck
import { MapPin, Mail, Phone } from 'lucide-solid';
import { Input } from '../atoms/Input';
import { TextArea } from '../atoms/TextArea';
import { Button } from '../atoms/Button';
import { SocialLinks } from '../atoms/SocialLinks';

export const ContactSection = (props) => (
  <section class="animate-in fade-in duration-500 max-w-4xl mx-auto w-full">
    <div class="bg-zinc-50 dark:bg-zinc-900/30 rounded-2xl p-8 border border-zinc-100 dark:border-transparent">
      <h2 class="text-2xl font-bold text-zinc-900 dark:text-zinc-100 mb-2">{props.uiText.contact.title}</h2>
      <p class="text-zinc-500 dark:text-zinc-400 mb-8">{props.uiText.contact.subtitle}</p>
      
      <div class="grid grid-cols-1 md:grid-cols-2 gap-12">
        {/* Form */}
        <form class="space-y-4" onSubmit={(e) => e.preventDefault()}>
          <Input id="name" label={props.uiText.placeholders.name} placeholder={props.uiText.placeholders.name} />
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Input id="email" type="email" label={props.uiText.placeholders.email} placeholder={props.uiText.placeholders.email} />
            <Input id="phone" type="tel" label={props.uiText.placeholders.phone} placeholder={props.uiText.placeholders.phone} />
          </div>
          <TextArea id="message" label={props.uiText.placeholders.message} placeholder={props.uiText.placeholders.message} />
          <Button class="w-full sm:w-auto">{props.uiText.buttons.send}</Button>
        </form>

        {/* Contact Info */}
        <div class="flex flex-col justify-center space-y-8 pl-0 md:pl-8 border-t md:border-t-0 md:border-l border-zinc-200 dark:border-zinc-800 pt-8 md:pt-0">
           <div>
             <h3 class="text-sm font-bold text-zinc-900 dark:text-zinc-100 mb-4">{props.uiText.sections.social}</h3>
             <SocialLinks links={props.profile.socialLinks} />
           </div>
           
           <div>
              <h3 class="text-sm font-bold text-zinc-900 dark:text-zinc-100 mb-4">{props.uiText.sections.location}</h3>
              <div class="flex items-center gap-2 text-zinc-500 dark:text-zinc-400 text-sm">
                <MapPin size={18} />
                <a 
                  href={`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(props.profile.location)}`} 
                  target="_blank" 
                  rel="noreferrer" 
                  class="hover:text-zinc-900 dark:hover:text-zinc-100 transition-colors"
                >
                  {props.profile.location}
                </a>
              </div>
           </div>

           <div>
              <h3 class="text-sm font-bold text-zinc-900 dark:text-zinc-100 mb-4">{props.uiText.sections.direct}</h3>
              <div class="flex flex-col gap-2 text-zinc-500 dark:text-zinc-400 text-sm">
                <a href={`mailto:${props.profile.email}`} class="flex items-center gap-2 hover:text-zinc-900 dark:hover:text-zinc-200 transition-colors">
                  <Mail size={18} /> {props.profile.email}
                </a>
                <a href={`tel:${props.profile.phone.replace(/\D/g, '')}`} class="flex items-center gap-2 hover:text-zinc-900 dark:hover:text-zinc-200 transition-colors">
                  <Phone size={18} /> {props.profile.phone}
                </a>
              </div>
           </div>
        </div>
      </div>
    </div>
  </section>
);
