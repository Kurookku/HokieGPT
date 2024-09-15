import Link from 'next/link';
import Image from 'next/image';

const Hero = () => {
  return (
    <div className="bg-white container pt-[30px] md:pt-[80px] pb-[100px] sm:pb-[100px] px-[22px] sm:px-0 mx-auto text-center">
      <div className="flex justify-center items-center pb-1">
          <Image
            src="/theme.png"
            alt="Step 1"
            width={800}
            height={500}
            className="flex justify-center items-center"
          />
      </div>
      <h2 className="text-center max-w-[867px] pb-5 sm:pb-7 text-[52px] sm:text-[100px] leading-[39.5px] tracking-[-1.04px] sm:leading-[75px] sm:tracking-[-2.74px] mx-auto sm:mt-12 mt-10">
        Chat with PDFs in your Prefered Learning Style!
      </h2>
      <p className="text-xl sm:text-2xl pb-10 sm:pb-8 leading-[19px] sm:leading-[34.5px] w-[232px] sm:w-full tracking-[-0.4px] sm:tracking-[-0.6px] text-center mx-auto">
        Have a conversation with your papers and textbooks as you want
      </p>
      <Link href={'/dashboard'}>
        <button className="bg-vt-burntOrange rounded-full sm:px-14 px-12 py-[2.5px] sm:py-4 text-white text-center text-xl sm:text-[30px] font-medium leading-[37px] tracking-[-0.3px]">
          Get Started
        </button>
      </Link>
      {/* <div className="flex justify-center items-center pt-[10px]">
        <a
          href="https://dub.sh/together-ai"
          target="_blank"
          rel="noreferrer"
          className="border border-black rounded-2xl py-1 px-4 text-slate-600 transition duration-300 ease-in-out sm:text-base text-sm cursor-pointer hover:text-slate-700"
        >
          Powered by <span className="font-bold">OpenAI </span>and{' '}
          <span className="font-bold">MongoDB</span>
      </a>
      </div> */}
    </div>
  );
};

export default Hero;
