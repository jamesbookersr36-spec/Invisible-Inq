import { useState } from 'react';
import { Link } from 'react-router-dom';
import DonationPopup from '../common/DonationPopup';
import CombinedStoryDropdown from '../story/CombinedStoryDropdown';

const Header = ({
  stories = [],
  currentStoryId = null,
  currentChapterId = null,
  currentSubstoryId = null,
  onStorySelect,
  onChapterSelect,
  onSubstorySelect,
  showStoryDropdown = false,
  usePlainLogo = false
}) => {
  const [showDonationPopup, setShowDonationPopup] = useState(false);

  return (
    <div className="sticky top-0 z-50 flex flex-col">
      {}
      <header className="bg-[#09090B] text-white shadow-md flex h-[42px] items-center relative">

        {}
        <div className={`h-full flex items-center ${showStoryDropdown ? 'ml-4' : 'ml-4 pl-2'}`}>
          <Link to="/" className="h-full flex items-center">
            <img
              src='/images/logo-with-text.png'
              alt="Invisible Injury Logo"
              className="h-6 object-contain ml-2"
              onError={(e) => {
                console.error("Image failed to load");
                e.target.classList.add('hidden');
              }}
            />
          </Link>
        </div>

        {}
        <nav className="absolute left-1/2 transform -translate-x-1/2 flex items-center">
          <Link
            to="/"
            className="text-white hover:text-gray-300 transition-colors text-xs lg:text-sm"
            aria-label="Home page"
            tabIndex={0}
          >
            Home Page
          </Link>
          <span className="mx-1 lg:mx-2 text-white text-xs lg:text-sm">-</span>
          <Link
            to="/about"
            className="text-white hover:text-gray-300 transition-colors text-xs lg:text-sm"
            aria-label="About page"
            tabIndex={0}
          >
            About
          </Link>
          <span className="mx-1 lg:mx-2 text-white text-xs lg:text-sm">-</span>
          <Link
            to="/contact"
            className="text-white hover:text-gray-300 transition-colors text-xs lg:text-sm"
            aria-label="Contact page"
            tabIndex={0}
          >
            Contact
          </Link>
          <span className="mx-1 lg:mx-2 text-white text-xs lg:text-sm">-</span>
          <button
            className="text-white hover:text-gray-300 transition-colors bg-transparent border-none p-0 cursor-pointer text-xs lg:text-sm"
            aria-label="Donate page"
            tabIndex={0}
            onClick={() => setShowDonationPopup(true)}
          >
            Donate
          </button>
        </nav>

        {}
        {showStoryDropdown && (
          <div className="hidden lg:flex items-center w-80 h-full justify-end ml-auto mr-4">
            <span className="text-white text-sm">Graph Viewer 1.0</span>
          </div>
        )}

        {}
        {!showStoryDropdown && (
          <div className="hidden lg:flex items-center pr-4 ml-auto mr-4">
            <span className="text-white text-sm">Graph Viewer 1.0</span>
          </div>
        )}

        {}
        {showDonationPopup && (
          <DonationPopup onClose={() => setShowDonationPopup(false)} />
        )}
      </header>

      {}
      {showStoryDropdown && (
        <div className="lg:hidden w-full bg-[#09090B] border-b border-[#707070] h-10 mt-0">
          <CombinedStoryDropdown
            stories={stories}
            selectedStoryId={currentStoryId}
            selectedChapterId={currentChapterId}
            selectedSubstoryId={currentSubstoryId}
            onStorySelect={onStorySelect}
            onChapterSelect={onChapterSelect}
            onSubstorySelect={onSubstorySelect}
            inHeader={false}
            isMobileFullWidth={true}
            placeholder="Select an Investigation"
          />
        </div>
      )}
    </div>
  );
};

export default Header;
