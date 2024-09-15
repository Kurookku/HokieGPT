import Logo from '../ui/Logo';
import Link from 'next/link';

const Footer = () => {
  return (
    <div className="border-t-[rgba(0,0,0,0.20)] border-t border-solid pt-4">
      <div className="container flex flex-col sm:flex-row justify-between items-center sm:h-[77px] pt-3 pb-6 sm:pt-0 px-2 sm:px-0 sm:space-y-0 space-y-4 mx-auto">
        <Logo />
        <span className="sm:text-xl text-lg sm:text-right text-center sm:w-full">
          Powered by{' '}
          <a
            href="https://openai.com/"
            target="_blank"
            className="font-semibold transition hover:text-black/50"
          >
            OpenAI
          </a>
          ,{' '}
          <a
            href="https://nextjs.org/"
            target="_blank"
            className=" font-semibold transition hover:text-black/50"
          >
            NextJS
          </a>
          ,{' '}
          <a
            href="https://www.mongodb.com/"
            target="_blank"
            className="font-semibold transition hover:text-black/50"
          >
            MongoDB
          </a>
          ,{' '}
          <a
            href="https://www.langchain.com/"
            target="_blank"
            className="font-semibold transition hover:text-black/50"
          >
            Langchain
          </a>
          .
        </span>
        <div className="flex items-center gap-[20px] sm:gap-[30px]">
          
        </div>
      </div>
    </div>
  );
};

export default Footer;
