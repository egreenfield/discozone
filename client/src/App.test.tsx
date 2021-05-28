import * as React from 'react';
import { render } from '@testing-library/react';
import { expect } from 'chai';
import App from './App';
import { Server } from './model/Server';

describe('<App >', () => {
  it('renders learn react link', () => {
    const { getByText } = render(<App server={new Server("")} />);
    const linkElement = getByText(/learn react/i);
    expect(document.body.contains(linkElement));
  });
});
