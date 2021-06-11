import { Button, SymbolCircleIcon, DeleteIcon, IconButton, Menu, MenuClosedIcon, MenuIcon, Popover, Position, StarIcon, CircleArrowUpIcon, RefreshIcon } from 'evergreen-ui';
import React, { useState, useEffect } from 'react';
import type { Server } from './model/Server';

export enum Action {
    ShowAll,
    ShowFavorite,
    ShowRejected,
    ShowUnwatched,
    Refresh,
    DeleteRejected
}

interface ActionMenuProps {
    server:Server;
    onSelect:(action:Action)=>void;
}


export const ActionMenu = ({server,onSelect}: ActionMenuProps) => {


    return (
        <Popover
        position={Position.BOTTOM_RIGHT}
        content={({ close }) => {
            function sendResult(action:Action) {
                onSelect(action);        
                close();
            }
            return (
            <Menu>
                <Menu.Group title="Filter">
                <Menu.Item onSelect={()=> sendResult(Action.ShowAll)} icon={CircleArrowUpIcon}>All</Menu.Item>
                <Menu.Item onSelect={()=> sendResult(Action.ShowFavorite)} icon={StarIcon}>Favorited</Menu.Item>
                <Menu.Item onSelect={()=> sendResult(Action.ShowRejected)} icon={DeleteIcon}>Rejected</Menu.Item>
                <Menu.Item onSelect={()=> sendResult(Action.ShowUnwatched)} icon={SymbolCircleIcon} secondaryText={<span>⌘R</span>}>
                    Unwatched
                </Menu.Item>
                </Menu.Group>
                <Menu.Divider />
                <Menu.Group title="Actions">
                <Menu.Item onSelect={()=> sendResult(Action.Refresh)} icon={RefreshIcon}>Refresh Dances</Menu.Item>
                <Menu.Item onSelect={()=> sendResult(Action.DeleteRejected)} icon={DeleteIcon} intent="danger">Delete Rejected Dances</Menu.Item>
                </Menu.Group>
            </Menu>
        )}}
        >
        <IconButton icon={MenuIcon} />
      </Popover>
    )
}
