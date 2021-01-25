import { When, Given } from 'cypress-cucumber-preprocessor/steps';

/** Acess the root url. */
const navigateToRoot = (): void => {
    cy.visit('');
};
Given(`I am on the root page`, navigateToRoot);

/** Assert header that welcomes the user. */
const assertWelcomed = (): void => {
    cy.findByRole('heading', { name: /welcome/i }).should('be.visible');
};
When(`I am welcomed`, assertWelcomed);
